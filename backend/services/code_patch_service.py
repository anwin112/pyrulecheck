import os
import shutil
import logging
from config import ENABLE_CODE_PATCHING, CREATE_FILE_BACKUP

logger = logging.getLogger(__name__)

def apply_code_patch(repo_path: str, relative_file_path: str, line_num: int, secure_code: str) -> bool:
    """
    Safely applies a code patch to a specific line in a file within the repository.
    Includes path traversal protection and automatic backups.
    """
    if not ENABLE_CODE_PATCHING:
        logger.warning(f"Code patching is disabled. Cannot patch {relative_file_path}")
        return False

    # Prevent directory traversal
    target_path = os.path.abspath(os.path.join(repo_path, relative_file_path))
    if not target_path.startswith(os.path.abspath(repo_path)):
        logger.error(f"Directory traversal attempt blocked: {relative_file_path}")
        return False

    if not os.path.exists(target_path):
        logger.error(f"Target file does not exist: {target_path}")
        return False

    backup_path = f"{target_path}.bak"
    
    try:
        if CREATE_FILE_BACKUP:
            shutil.copy2(target_path, backup_path)

        with open(target_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if line_num < 1 or line_num > len(lines):
            logger.error(f"Invalid line number {line_num} for file {target_path}")
            return False

        # Calculate indentation to preserve it
        original_line = lines[line_num - 1]
        indentation = original_line[:len(original_line) - len(original_line.lstrip())]
        
        # Format the secure code
        secure_lines = secure_code.splitlines()
        formatted_secure_code = "\n".join([(indentation + line if line.strip() else line) for line in secure_lines]) + "\n"

        # Replace the line
        lines[line_num - 1] = formatted_secure_code

        with open(target_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        logger.info(f"Successfully patched {relative_file_path} at line {line_num}")
        return True

    except Exception as e:
        logger.error(f"Failed to apply patch to {target_path}: {str(e)}")
        # Restore backup if something went wrong during the write
        if CREATE_FILE_BACKUP and os.path.exists(backup_path):
            try:
                shutil.copy2(backup_path, target_path)
                logger.info(f"Restored backup for {target_path}")
            except Exception as restore_err:
                logger.error(f"Failed to restore backup for {target_path}: {str(restore_err)}")
        return False
