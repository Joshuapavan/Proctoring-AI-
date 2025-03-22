from sqlalchemy.orm import Session
from datetime import datetime
from models.logs import Log
from utils.logger import logger

class LogService:
    @staticmethod
    async def store_logs(db: Session, user_id: int, logs: list) -> list:
        if not logs:
            return []

        logger.info(f"Attempting to store {len(logs)} logs for user {user_id}")
        log_entries = []

        try:
            # Create all log entries first
            for log_entry in logs:
                try:
                    db_log = Log(
                        log=log_entry["event"],
                        event_type=log_entry["event"].lower().replace(" ", "_"),
                        timestamp=datetime.utcnow(),
                        user_id=user_id
                    )
                    log_entries.append(db_log)
                    logger.debug(f"Created log entry: {log_entry}")
                except Exception as e:
                    logger.error(f"Error creating log entry: {str(e)}")
                    continue

            if log_entries:
                try:
                    # Add all entries to session
                    for entry in log_entries:
                        db.add(entry)
                    
                    # Commit transaction
                    db.flush()  # Flush changes to DB
                    db.commit()  # Commit transaction
                    logger.info(f"Successfully stored {len(log_entries)} logs")
                    
                    # Refresh entries to get their IDs
                    for entry in log_entries:
                        db.refresh(entry)
                        
                    return log_entries
                except Exception as e:
                    logger.error(f"Database error: {str(e)}", exc_info=True)
                    db.rollback()
                    return []

        except Exception as e:
            logger.error(f"Transaction error: {str(e)}", exc_info=True)
            if 'db' in locals():
                db.rollback()
            return []

        return []
