# database.py
import sqlite3

DATABASE_NAME = 'credit_cards.db'


def init_db():
    """Initializes the SQLite database and creates the credit_cards table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credit_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            issuer TEXT NOT NULL,
            joining_fee REAL NOT NULL,
            annual_fee REAL NOT NULL,
            reward_type TEXT NOT NULL,
            reward_rate REAL NOT NULL,
            eligibility_income REAL NOT NULL,
            eligibility_credit_score INTEGER NOT NULL,
            special_perks TEXT,
            affiliate_link TEXT,
            image_url TEXT,
            UNIQUE(name, issuer) ON CONFLICT IGNORE
        )
    ''')
    conn.commit()
    conn.close()


def add_card(
    name, issuer, joining_fee, annual_fee, reward_type, reward_rate,
    eligibility_income, eligibility_credit_score, special_perks,
    affiliate_link, image_url
):
    """Inserts a new credit card into the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO credit_cards (
            name, issuer, joining_fee, annual_fee, reward_type, reward_rate,
            eligibility_income, eligibility_credit_score, special_perks,
            affiliate_link, image_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        name, issuer, joining_fee, annual_fee, reward_type, reward_rate,
        eligibility_income, eligibility_credit_score, special_perks,
        affiliate_link, image_url
    ))
    conn.commit()
    conn.close()


def get_cards_by_criteria(min_income, min_credit_score, preferred_benefits_list):
    """
    Fetches credit cards from the database that match the given criteria.
    If preferred_benefits_list is empty, it returns all cards matching income and credit score.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    query = "SELECT * FROM credit_cards WHERE eligibility_income <= ? AND eligibility_credit_score <= ?"
    params = [min_income, min_credit_score]

    if preferred_benefits_list:
        # Construct dynamic WHERE clause for benefits
        benefit_conditions = []
        for benefit in preferred_benefits_list:
            benefit_conditions.append(
                f"(special_perks LIKE ? OR reward_type LIKE ?)")
            # Match in special_perks or reward_type
            params.extend([f"%{benefit}%", f"%{benefit}%"])

        # Use 'OR' to match any of the preferred benefits
        query += " AND (" + " OR ".join(benefit_conditions) + ")"

    cursor.execute(query, params)
    cards = cursor.fetchall()
    conn.close()
    return cards


def clear_duplicate_cards():
    """
    Removes duplicate credit card entries from the database, keeping one instance.
    Duplicates are identified by matching 'name' and 'issuer'.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Create a temporary table with unique rows
    cursor.execute('''
        CREATE TEMPORARY TABLE IF NOT EXISTS temp_credit_cards AS
        SELECT * FROM credit_cards GROUP BY name, issuer;
    ''')

    # Clear the original table
    cursor.execute('DELETE FROM credit_cards;')

    # Insert unique rows back into the original table
    cursor.execute('INSERT INTO credit_cards SELECT * FROM temp_credit_cards;')

    # Drop the temporary table
    cursor.execute('DROP TABLE temp_credit_cards;')

    conn.commit()
    conn.close()
    print("Duplicate entries removed from the database.")


def populate_initial_data():
    """
    Populates the database with initial dummy credit card data if the database is empty.
    This prevents re-adding data on every run after the initial setup.
    """
    # Check if any cards exist by performing a broad query
    # Using a simple check like this avoids re-adding data multiple times
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM credit_cards")
    count = cursor.fetchone()[0]
    conn.close()

    if count == 0:
        print("Adding dummy data...")
        add_card("HDFC Diners Club Black Metal Edition Credit Card", "HDFC Bank", 10000, 10000, "Travel Points", 0.0333, 60000, 750,
                 "Unlimited airport lounge access (primary & add-on), High base rewards rate, 10X reward points on SmartBuy, 2X on weekend dining, 1:1 redemption, Club Marriott, Amazon, Swiggy One annual memberships, Low forex markup fee 2%, 10000 RP on Rs. 4 lakh spend per quarter, 6 complimentary golf games per quarter", "#", "https://www.paisabazaar.com/wp-content/uploads/2024/04/HDFC-Diners-Club-Black-Credit-Card.png")
        add_card("Axis Bank Reserve Credit Card", "Axis Bank", 50000, 50000, "Travel Points", 0.04, 70000, 760,
                 "Unlimited domestic & international lounge visits via Priority Pass, Low forex mark-up fee 1.5%, 2X reward points on international spends, Up to 30 EDGE reward points for every Rs. 200 spent, B1G1 BookMyShow tickets, ITC Culinaire, Accorplus, Club Marriott & EazyDiner Prime memberships, 50 free golf rounds/year", "#", "https://www.paisabazaar.com/wp-content/uploads/2022/03/Axis-Reserve-Credit-Card.png")
        add_card("Axis Atlas Credit Card", "Axis Bank", 5000, 5000, "Travel Points", 0.05, 35000, 700,
                 "2.5X EDGE Miles on Travel, Up to 12 international and 18 domestic lounge access per year, Up to 2,500 bonus EDGE Miles as welcome benefit, Up to 5 EDGE Miles per Rs. 100 spent on travel, Redeem EDGE Miles at value of 1 EDGE Mile = 2 Partner Points, Milestone benefits up to 5,000 EDGE Miles", "#", "https://www.paisabazaar.com/wp-content/uploads/2023/02/Axis-Atlas-1-300x190.png")
        add_card("HDFC Regalia Gold Credit Card", "HDFC Bank", 2500, 2500, "Rewards", 0.0267, 30000, 710, "5X reward points on Nykaa, Myntra, Marks & Spencer and Reliance Digital, 4 reward points per Rs. 150 across all retail spends, Complimentary Swiggy One & MMT Black Elite Memberships, Gift voucher Rs. 2,500 on joining fee payment, 6 complimentary international lounge visits, 12 complimentary domestic airport lounge visits per year, Marks & Spencer/ Reliance Digital/ Myntra/ Marriott vouchers on quarterly spends, Flight vouchers on annual spends", "#", "https://www.paisabazaar.com/wp-content/uploads/2023/03/HDFC-Regalia-Gold-Credit-Card.png")
        add_card("YES Bank Paisabazaar PaisaSave Credit Card", "YES Bank", 0, 499, "Cashback", 0.015, 15000, 650, "3% Cashback Points on e-commerce spends (max 5,000 points/month), Unlimited 1.5% Cashback Points on all other spends, including UPI, Redeemable as statement credit 1:1, Renewal fee waived on Rs. 1.2 lakh annual spends, 1% fuel surcharge waiver",
                 "#", "https://www.paisabazaar.com/wp-content/uploads/2024/08/YES-Bank-Paisabazaar-PaisaSave-Credit-Card.png")
        add_card("Cashback SBI Card", "SBI Card", 999, 999, "Cashback", 0.01, 20000, 670, "5% cashback on all online spends (no merchant restriction), 1% cashback across all offline spends, Cashback up to Rs. 5,000 per month, Renewal fee reversed on Rs. 2 lakh annual spend, 1% fuel surcharge waiver",
                 "#", "https://www.paisabazaar.com/wp-content/uploads/2022/04/Cashback-SBI-Card.png")
        add_card("HSBC TravelOne Credit Card", "HSBC", 4999, 4999, "Travel Points", 0.02, 30000, 700, "2x rewards on all travel bookings, Up to 20% off on Zomato, Yatra, EaseMyTrip, Cashback Rs. 1,000, Postcard Hotels voucher Rs. 3,000, 3 months EazyDiner Prime, 4 reward points on every Rs. 100 spent on flights/travel aggregators/foreign currency, 2 reward points on every Rs. 100 other categories, 1 reward point = 1 Air Mile or Hotel Point, 10,000 bonus RP on Rs. 12 lakh annual spend, 6 domestic and 4 international airport lounge access, 4 rounds and 12 golf lessons/year, Up to 20% off duty-free shopping via AdaniOne", "#", "https://www.paisabazaar.com/wp-content/uploads/2025/01/HSBC-TravelOne-Credit-Card.png")
        add_card("Axis Bank SELECT Credit Card", "Axis Bank", 3000, 3000, "Rewards", 0.05, 28000, 690, "2X EDGE Reward Points across all retail transactions, 10,000 EDGE Reward Points welcome benefit, Flat Rs. 500 off per month on BigBasket, Rs. 200 off on Swiggy twice a month, Up to 12 complimentary international lounge visits, 2 domestic lounge visits per quarter, Up to 12 complimentary golf rounds",
                 "#", "https://www.paisabazaar.com/wp-content/uploads/2015/11/Axis-Bank-Select-Credit-Card.png")
        add_card("Tata Neu Infinity HDFC Bank Credit Card", "HDFC Bank", 1499, 1499, "Co-branded", 0.015, 22000, 680,
                 "Up to 10% value-back on Tata Neu spends, 8 domestic and 4 international Priority Pass lounge access per year, 5% NeuCoins on all non-EMI spends at Tata Neu & its partner brands, Additional 5% NeuCoins on select spends, 1.5% NeuCoins on UPI/non-Tata/merchant EMI, 1,499 NeuCoins after first spend, Low forex markup fee 2%", "#", "https://www.paisabazaar.com/wp-content/uploads/2017/10/Tata-Neu-Infinity-HDFC-Bank-Credit-Card.png")
        add_card("IndianOil RBL Bank XTRA Credit Card", "RBL Bank", 1500, 1500, "Fuel", 0.075, 15000, 660, "Up to 8.5% savings on IOCL fuel spends, 1,000 Fuel Points on reaching Rs. 75,000 quarterly spends, 15 Fuel Points per Rs. 100 on IOCL fuel, 1% fuel surcharge waiver (Rs. 500-4000), 2 Fuel Points per Rs. 100 other categories, 1 Fuel Point = Rs. 0.50 for IOCL fuel, 3,000 Fuel Points welcome benefit, Annual Fee waived on Rs. 2.75 lakh annual spends",
                 "#", "https://www.paisabazaar.com/wp-content/uploads/2024/08/IndianOil-RBL-Bank-Credit-Cards.webp")
        add_card("SBI Prime Credit Card", "SBI Card", 2999, 2999, "Rewards", 0.02, 25000, 700, "10 reward points per Rs. 100 on dining, groceries, movies and departmental stores, E-gift vouchers worth Rs. 3,000 welcome benefit, Complimentary Club Vistara membership, Complimentary international and domestic lounge access",
                 "#", "https://www.paisabazaar.com/wp-content/uploads/2022/01/sbi-prime-cardface.png")
        add_card("American Express Membership Rewards Credit Card", "American Express", 1000, 4500, "Rewards", 0.02, 30000, 720, "1 Membership Reward point per Rs. 50, Bonus 5,000 Membership Rewards points upon First Year Card Renewal, Redemption options cover everyday brands like Flipkart & Amazon to premium ones like Tanishq and Taj, 4,000 Membership Rewards Points on card activation, Monthly milestone benefits",
                 "#", "https://www.paisabazaar.com/wp-content/uploads/2024/06/American-Express-Membership-Rewards%C2%AE-Credit-Card.png")
        add_card("HDFC MoneyBack+ Credit Card", "HDFC Bank", 500, 500, "Cashback", 0.0133, 15000, 650, "10X CashPoints on Amazon, BigBasket, Flipkart, Reliance Smart SuperStore & Swiggy, 2 CashPoints per Rs. 150 on other spends, 500 cashpoints on card activation, Quarterly milestone benefit",
                 "#", "https://www.paisabazaar.com/wp-content/uploads/2022/08/HDFC-MoneyBack-Plus-Credit-Card.png")
        add_card("Axis Bank Horizon Credit Card", "Axis Bank", 3000, 3000, "Travel Points", 0.05, 35000, 700,
                 "5 EDGE Miles per Rs. 100 spent on Travel EDGE portal and at direct airline websites/counters, 1 EDGE Mile = 1 Partner Point, 8 complimentary visits to international and up to 32 to domestic airport lounges per year", "#", "https://www.paisabazaar.com/wp-content/uploads/2024/06/Axis-Bank-Horizon-Credit-Card.png")
        add_card("American Express Platinum Travel Credit Card", "American Express", 5000, 5000, "Travel Points", 0.02, 40000, 730,
                 "1 Membership Rewards Point for every Rs. 50 spent, 8 domestic lounge visits per year, 25,000 Membership Rewards Points and Taj Stay voucher worth Rs. 10,000 on spending Rs. 4 Lakh in a year", "#", "https://www.paisabazaar.com/wp-content/uploads/2024/06/American-Express%C2%AE-Platinum-Travel-Credit-Card.png")
        add_card("MakeMyTrip ICICI Bank Credit Card", "ICICI Bank", 999, 999, "Travel", 0.01, 20000, 680, "Unlimited 6% myCash on hotel bookings via MakeMyTrip, Unlimited 3% myCash on flights, holiday packages, cabs & bus bookings via MakeMyTrip, 1% myCash on all other spends, Low forex markup fee of 0.99%, Lounge access is not spend-based, 25 myCash on every train booking via MakeMyTrip, Joining and renewal benefits via MMT voucher and Gold memberships",
                 "#", "https://www.paisabazaar.com/wp-content/uploads/2017/10/MakeMyTrip-ICICI-Credit-Card.png")
        add_card("HDFC Infinia Credit Card – Metal Edition", "HDFC Bank", 12500, 12500, "Rewards", 0.0333, 80000, 780,
                 "Invite-only, All-in-one benefits (travel, shopping, movies etc.), Complimentary Club Marriott membership, Complimentary luxury hotel membership, 1+1 complimentary weekend buffet at ITC hotels, Unlimited lounge access worldwide, Low forex markup fee 2%, Unlimited complimentary golf games", "#", "https://www.paisabazaar.com/wp-content/uploads/2017/10/HDFC-infinia-metal-edition.jpg")
        add_card("American Express Platinum Card", "American Express", 66000, 66000, "Premium", 0.01, 100000, 790, "Stay vouchers Rs. 45,000 from Taj/SeleQtions/Vivanta Hotels, Excellent golf benefit, Multiple hotel memberships (Accor Plus, I Prefer, Marriott Bonvoy, Hilton Honors, Taj Reimagined), Exclusive deals on airlines (Qatar, Air France, Emirates etc.), World-class Platinum concierge service, Unlimited airport lounge access, VIP-only event invitations",
                 "#", "https://www.paisabazaar.com/wp-content/uploads/2022/11/American-Express-Platinum-Credit-Card.png")
        add_card("ICICI Bank Emeralde Private Metal Credit Card", "ICICI Bank", 12499, 12499, "Rewards", 0.06, 75000, 770, "Complimentary memberships to Taj Epicure, EazyDiner Prime and Priority Pass Program, 1:1 redemption ratio for reward points, Unlimited access to golf lessons or rounds, Unlimited domestic & international lounges at select airports, Low forex markup fee 2%, Buy one get one ticket free on BookMyShow, Overall benefits on dining/movies/entertainment/golf/travel, Exclusive concierge services",
                 "#", "https://www.paisabazaar.com/wp-content/uploads/2023/10/ICICI-Bank-Emeralde-Private-Metal-Credit-Card-300x190.webp")
        add_card("BPCL SBI Card Octane", "SBI Card", 1499, 1499, "Fuel", 0.01, 15000, 660, "7.25% value back on BPCL fuel purchases, 6,000 bonus reward points welcome benefit, 1% surcharge waiver across all BPCL petrol pumps, Additional benefits like complimentary lounge visit, fraud liability cover, 25 reward points for every Rs. 100 spent at BPCL Fuel, Lubricants & Bharat Gas, Instant reward redemption at select BPCL petrol pumps",
                 "#", "https://www.paisabazaar.com/wp-content/uploads/2020/11/BPCL-SBI-Card-Octane-300x197.png")
        add_card("IDFC FIRST Power+ Credit Card", "IDFC FIRST Bank", 499, 499, "Fuel", 0.02, 12000, 640,
                 "5% savings as 30 rewards points per Rs. 150 spends on HPCL fuel purchase, 5% savings as 30 Reward points per Rs. 150 spends on groceries and utilities, Uncapped 3 reward points per Rs. 150 on all other eligible spends, Happy Coins via HP Pay App", "#", "https://www.paisabazaar.com/wp-content/uploads/2023/04/hpcl-power-plus.jpg")
        add_card("ICICI HPCL Super Saver Credit Card", "ICICI Bank", 500, 500, "Fuel", 0.02, 10000, 630, "Up to 5% value back on HPCL fuel, 4% cashback on fuel spends at HPCL pumps, 5% back as reward points on grocery, departmental stores and utility bill spends, 2 reward points on every Rs. 100 spent on retail purchases",
                 "#", "https://www.paisabazaar.com/wp-content/webp-express/webp-images/doc-root/wp-content/uploads/2021/12/ICICI-Bank-HPCL-Super-Saver-Credit-Card-300x190.png.webp")
        add_card("IndianOil Axis Bank Credit Card", "Axis Bank", 500, 500, "Fuel", 0.01, 10000, 630,
                 "4% value back on fuel spends at any IOCL outlet, 1% value back on online shopping, EDGE rewards equivalent to 1st fuel spend up to Rs. 250 welcome bonus, Discount on booking movie tickets via BookMyShow, Discount on dining bills at partner restaurants", "#", "https://www.paisabazaar.com/wp-content/uploads/2019/12/Indianoil-Axis.jpg")
        print("Dummy data added successfully.")
    else:
        print("Database already contains data, skipping dummy data addition.")
    conn.close()  # Close connection after usage
