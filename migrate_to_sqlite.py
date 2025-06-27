import os
import sys
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add parent directory to Python path so we can use absolute imports from /api
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from api.models.database_models import Base, Message, Agent

def migrate_database():
    """
    Migrates data from a MySQL database to a SQLite database.
    """
    load_dotenv()

    # --- 1. Setup Database Connections ---
    mysql_url = os.environ.get("MYSQL_DB")
    if not mysql_url:
        print("Error: MYSQL_DB environment variable not set.")
        return

    # Adjust for SQLAlchemy 2.0 async dialect if present
    if mysql_url.startswith("mysql://"):
        mysql_url = mysql_url.replace("mysql://", "mysql+mysqlconnector://", 1)

    sqlite_path = os.path.join("data", "local.db")
    sqlite_url = f"sqlite:///{sqlite_path}"

    print(f"Source (MySQL): {mysql_url.split('@')[-1]}")
    print(f"Destination (SQLite): {sqlite_url}")

    try:
        mysql_engine = create_engine(mysql_url)
        sqlite_engine = create_engine(sqlite_url)
    except Exception as e:
        print(f"Error creating database engines: {e}")
        return

    MySQLSession = sessionmaker(bind=mysql_engine)
    SQLiteSession = sessionmaker(bind=sqlite_engine)

    # --- 2. Create Tables in SQLite ---
    print("Creating tables in SQLite database...")
    Base.metadata.create_all(sqlite_engine)
    print("Tables created successfully.")

    mysql_session = MySQLSession()
    sqlite_session = SQLiteSession()

    try:
        # --- 3. Migrate Agents ---
        print("Migrating 'agents' table...")
        agents = mysql_session.execute(select(Agent)).scalars().all()
        if agents:
            for agent in agents:
                # Create a new Agent object for the new session
                new_agent = Agent(
                    id=agent.id,
                    user_id=agent.user_id,
                    messages=agent.messages,
                    created_at=agent.created_at,
                )
                sqlite_session.merge(new_agent)
            sqlite_session.commit()
            print(f"Successfully migrated {len(agents)} agents.")
        else:
            print("No records found in 'agents' table to migrate.")

        # --- 4. Migrate Messages ---
        print("Migrating 'messages' table...")
        messages = mysql_session.execute(select(Message)).scalars().all()
        if messages:
            for message in messages:
                new_message = Message(
                    id=message.id,
                    user_id=message.user_id,
                    msg_content=message.msg_content,
                    type=message.type,
                    thread_name=message.thread_name,
                    sender_name=message.sender_name,
                    timestamp=message.timestamp,
                    agent_id=message.agent_id,
                    created_at=message.created_at,
                )
                sqlite_session.merge(new_message)
            sqlite_session.commit()
            print(f"Successfully migrated {len(messages)} messages.")
        else:
            print("No records found in 'messages' table to migrate.")

        print("\nDatabase migration completed successfully!")

    except Exception as e:
        print(f"\nAn error occurred during migration: {e}")
        sqlite_session.rollback()
    finally:
        mysql_session.close()
        sqlite_session.close()
        print("Database sessions closed.")

if __name__ == "__main__":
    # Create the data directory if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")
    migrate_database() 