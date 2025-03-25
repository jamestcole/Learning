import os
import time
import schedule
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackService:
    def __init__(self):
        self.__web_client = self.__get_web_client()

    def send_message_to_channel(self, channel_id: str, message: str) -> None:
        try:
            response = self.__web_client.chat_postMessage(channel=channel_id, text=message)
            print(f"Message posted to {channel_id}: {response['message']['text']}")
        except SlackApiError as e:
            print(f"Error posting message: {e.response['error']}")

    def list_all_channels(self):
        try:
            # List all channels the bot is a part of
            response = self.__web_client.conversations_list(types="public_channel,private_channel")
            channels = response['channels']
            
            # Print all available channels and their IDs
            print("Available Channels:")
            for channel in channels:
                print(f"Channel Name: {channel['name']} | Channel ID: {channel['id']}")
        except SlackApiError as e:
            print(f"Error fetching channels: {e.response['error']}")

    def get_channel_id_by_name(self, channel_name: str) -> str:
        try:
            # List all channels the bot is a part of
            response = self.__web_client.conversations_list(types="public_channel,private_channel")
            channels = response['channels']
            
            # Find the channel with the specified name
            for channel in channels:
                if channel['name'] == channel_name:
                    return channel['id']
            print(f"Channel {channel_name} not found.")
            return ""
        except SlackApiError as e:
            print(f"Error fetching channels: {e.response['error']}")
            return ""

    def __get_web_client(self) -> WebClient:
        slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
        if not slack_bot_token:
            raise ValueError("SLACK_BOT_TOKEN environment variable is not set.")
        return WebClient(token=slack_bot_token)

    def post_daily_update(self, channel_id: str, update_message: str) -> None:
        """Post a daily update to the specified channel."""
        self.send_message_to_channel(channel_id, update_message)

# Main function
def main():
    # Initialize SlackService instance
    slack_service = SlackService()

    # List all available channels first
    slack_service.list_all_channels()

    # Get the channel ID for 'learning-envteam'
    channel_id = slack_service.get_channel_id_by_name("server-env-dm")

    if channel_id:
        # Schedule a daily message at a specific time (for example, every day at 9:00 AM)
        def daily_update():
            slack_service.post_daily_update(channel_id, "This is your daily update!")

        # Schedule the daily update
        schedule.every().day.at("09:00").do(daily_update)

        print("Scheduled daily update at 09:00 AM.")

        # Run the scheduler
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        print("Failed to find the channel. Exiting.")

if __name__ == "__main__":
    main()
