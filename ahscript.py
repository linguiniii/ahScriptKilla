import requests
import time
import sys
import os

# Get configuration from environment variables
API_KEY = os.getenv('HYPIXEL_API_KEY')
PLAYER_UUID = os.getenv('PLAYER_UUID')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

# Validate that all required environment variables are set
if not API_KEY:
    print("Error: HYPIXEL_API_KEY environment variable is not set")
    sys.exit(1)
if not PLAYER_UUID:
    print("Error: PLAYER_UUID environment variable is not set")
    sys.exit(1)
if not DISCORD_WEBHOOK_URL:
    print("Error: DISCORD_WEBHOOK_URL environment variable is not set")
    sys.exit(1)

def get_auction_data():
    """Fetch auction data from the SkyBlock API."""
    try:
        url = f"https://api.hypixel.net/skyblock/auctions?key={API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            auctions = data.get('auctions', [])
            print(f"Retrieved {len(auctions)} auctions from API")
            return auctions
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
            # Check if auction has ended (claimed or past end time)
            current_time = int(time.time() * 1000)  # Convert to milliseconds
            auction_ended = auction.get('claimed', False) or current_time > auction.get('end', float('inf'))
            
            if auction_ended:
                item_name = auction.get('item_name', 'Unknown Item')
                auction_id = auction['uuid']
                price = auction.get('highest_bid_amount', auction.get('starting_bid', 0))

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
    
    # Send startup notification to Discord
    try:
        startup_data = {
            "content": "🚀 **Auction Monitor Started!**\nYour Hypixel SkyBlock auction monitoring script is now running and will notify you of completed auctions."
        }
        response = requests.post(DISCORD_WEBHOOK_URL, json=startup_data)
        if response.status_code == 204:
            print("Startup notification sent to Discord successfully!")
        else:
            print(f"Error sending startup notification: {response.status_code}")
    except Exception as e:
        print(f"Error sending startup notification: {e}")
    seen_auctions = set()  # Keep track of auctions we've already processed
    try:
        while True:
            print("Checking auctions...")
            auction_data = get_auction_data()
            if auction_data:
                for auction in auction_data:
                    auction_id = auction['uuid']
                    # Only process auctions from your account
                    if auction.get('auctioneer') != PLAYER_UUID:
                        continue
                    # Only process auctions that haven't been sold before
                    # Check if auction has ended (claimed or past end time)
                    current_time = int(time.time() * 1000)  # Convert to milliseconds
                    auction_ended = auction.get('claimed', False) or current_time > auction.get('end', float('inf'))
                    
                    if auction_ended and auction_id not in seen_auctions:
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
