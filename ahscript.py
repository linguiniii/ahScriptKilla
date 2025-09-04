import requests
import time
import sys

# Replace these with your own information
API_KEY = '97eccbcc-43fa-44a3-be49-54851921b866'
PLAYER_UUID = 'ef548534aa7d48b59e34aaf8d900b33a'
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1413226690351730780/TdqoSyeyW9Qq_ZYfiqtAwTcc93w1-nHsBrLVeWphTbGNccNRHrqCDhKn18ktW2hko6QJ'

def get_auction_data():
    """Fetch auction data from the SkyBlock API."""
    try:
        url = f"https://api.hypixel.net/skyblock/auctions?key={API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get('auctions', [])
        else:
            print(f"Error fetching data: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error in get_auction_data: {e}")
        return []

def check_auction_status(auction_data):
    """Check the auction status and send notifications for sold auctions."""
    try:
        for auction in auction_data:
            if auction['auctionEnded']:  # If auction has ended
                item_name = auction['item_name']
                auction_id = auction['auctionId']
                price = auction['price']

                # Send notification for this sold auction
                print(f"Auction for {item_name} (ID: {auction_id}) has been sold for {price} coins!")
                send_discord_notification(item_name, auction_id, price)
    except Exception as e:
        print(f"Error in check_auction_status: {e}")

def send_discord_notification(item_name, auction_id, price):
    """Send a notification to Discord using a webhook."""
    try:
        data = {
            "content": f"**Auction Sold!**\nYour auction for **{item_name}** (ID: {auction_id}) has been sold for **{price}** coins!",
        }
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print("Discord notification sent successfully!")
        else:
            print(f"Error sending Discord notification: {response.status_code}")
    except Exception as e:
        print(f"Error in send_discord_notification: {e}")

def main():
    """Main loop to check auction status periodically."""
    print("Script has started...")  # Notify that the script has started
    seen_auctions = set()  # Keep track of auctions we've already processed
    try:
        while True:
            print("Checking auctions...")
            auction_data = get_auction_data()
            if auction_data:
                for auction in auction_data:
                    auction_id = auction['auctionId']
                    # Only process auctions that haven't been sold before
                    if auction['auctionEnded'] and auction_id not in seen_auctions:
                        seen_auctions.add(auction_id)
                        check_auction_status([auction])
            time.sleep(60)  # Wait 60 seconds before checking again
    except KeyboardInterrupt:
        print("\nScript has stopped.")  # Notify that the script has stopped
        sys.exit(0)
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    main()