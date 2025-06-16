# recommender.py

def get_card_recommendations(raw_cards: list[dict], user_data: dict) -> list[dict]:
    """
    Processes a list of raw credit card data, calculates estimated annual rewards,
    generates key reasons for recommendation, and returns a ranked list of top cards.

    Args:
        raw_cards: A list of dictionaries, where each dictionary represents a credit card
                   with all its details (name, reward_type, special_perks, fees, etc.).
        user_data: A dictionary containing user's collected information like
                   'spending_habits', 'preferred_benefits'.

    Returns:
        A list of dictionaries, where each dictionary represents a recommended card
        with 'card_name', 'image_url', 'key_reasons', 'reward_simulation',
        'net_benefit', and 'affiliate_link'. The list is sorted by 'net_benefit'
        in descending order, limited to the top 5 unique cards.
    """
    ranked_cards = []

    # Calculate total spending from all categorized habits
    total_monthly_spending = sum(user_data['spending_habits'].values())

    # Convert preferred_benefits to a set for faster lookup
    user_preferred_benefits_set = set(user_data['preferred_benefits'])

    for card in raw_cards:
        estimated_annual_rewards = 0
        key_reasons = []

        # --- Base reward calculation and reason generation based on reward_type ---
        reward_type_lower = card['reward_type'].lower()
        special_perks_lower = card['special_perks'].lower()

        if reward_type_lower == 'cashback':
            estimated_annual_rewards += (total_monthly_spending *
                                         card['reward_rate'] * 12)
            key_reasons.append(
                f"Offers a solid base cashback of {card['reward_rate']*100:.2f}% on general spends.")
            if 'online spends' in special_perks_lower:
                online_spends = user_data['spending_habits'].get('dining', 0) + \
                    user_data['spending_habits'].get('entertainment', 0) + \
                    user_data['spending_habits'].get('groceries', 0) + \
                    user_data['spending_habits'].get('travel', 0)
                # Additional 1% for online
                estimated_annual_rewards += (online_spends * 0.01 * 12)
                key_reasons.append(
                    "Provides enhanced cashback for your online spending habits.")

        elif reward_type_lower == 'travel points':
            estimated_annual_rewards += (total_monthly_spending *
                                         card['reward_rate'] * 12) * 0.5
            key_reasons.append(
                "Earns valuable travel points, ideal for your travel preferences.")

        elif reward_type_lower == 'rewards':
            estimated_annual_rewards += (total_monthly_spending *
                                         card['reward_rate'] * 12) * 0.35
            key_reasons.append(
                "Offers versatile reward points for various redemption options.")
            if 'dining' in user_data['spending_habits'] and 'dining' in special_perks_lower:
                key_reasons.append("Accelerated rewards on dining expenses.")
            if 'groceries' in user_data['spending_habits'] and 'groceries' in special_perks_lower:
                key_reasons.append("Accelerated rewards on grocery purchases.")
            if 'movies' in special_perks_lower and ('entertainment' in user_data['spending_habits'] or 'outings/activities' in user_data['spending_habits'].keys()):
                key_reasons.append(
                    "Provides good benefits for movie and entertainment spends.")

        elif reward_type_lower == 'co-branded':
            if 'tata neu' in card['name'].lower() and ('dining' in user_data['spending_habits'] or 'groceries' in user_data['spending_habits']):
                estimated_annual_rewards += (user_data['spending_habits'].get(
                    'dining', 0) + user_data['spending_habits'].get('groceries', 0)) * 0.05 * 12
                key_reasons.append(
                    "Offers significant value-back on Tata Neu and its partner brands.")
            elif 'amazon pay icici' in card['name'].lower() and 'online shopping' in user_preferred_benefits_set:
                online_shopping_spends = user_data['spending_habits'].get(
                    'dining', 0) + user_data['spending_habits'].get('groceries', 0) + user_data['spending_habits'].get('entertainment', 0)
                estimated_annual_rewards += online_shopping_spends * 0.03 * 12
                key_reasons.append(
                    "Excellent for Amazon spending and general online shopping, matching your preferences.")
            else:
                estimated_annual_rewards += (total_monthly_spending *
                                             card['reward_rate'] * 12) * 0.6
                key_reasons.append(
                    "Provides specialized co-branded benefits and rewards.")

        elif reward_type_lower == 'fuel':
            fuel_spending = user_data['spending_habits'].get('fuel', 0)
            if fuel_spending > 0:
                estimated_annual_rewards += (fuel_spending *
                                             card['reward_rate'] * 12)
                key_reasons.append(
                    f"Offers substantial savings on fuel (approx. {card['reward_rate']*100:.2f}% value back).")
            else:
                key_reasons.append(
                    "Primarily a fuel card, but offers other general benefits suitable for your profile.")

        # --- Add reasons based on preferred benefits matching card perks (more flexible) ---
        if 'lounge access' in user_preferred_benefits_set and 'lounge access' in special_perks_lower:
            key_reasons.append("Includes valuable airport lounge access.")
        if 'travel' in user_preferred_benefits_set and ('travel points' in reward_type_lower or 'travel' in special_perks_lower):
            if "Strong travel benefits, including lounge access." not in key_reasons:  # Avoid duplication
                key_reasons.append(
                    "Features strong travel benefits, including potential lounge access.")
        if 'cashback' in user_preferred_benefits_set and 'cashback' in reward_type_lower:
            if "Provides good cashback opportunities." not in key_reasons:  # Avoid duplication
                key_reasons.append(
                    "Offers good cashback opportunities on your spends.")
        if 'amazon vouchers' in user_preferred_benefits_set and 'amazon vouchers' in special_perks_lower:
            key_reasons.append("Comes with valuable Amazon vouchers.")
        if 'dining' in user_preferred_benefits_set and 'dining' in special_perks_lower:
            if "Great for dining discounts/rewards." not in key_reasons:  # Avoid duplication
                key_reasons.append("Ideal for dining discounts and rewards.")
        if 'movies' in user_preferred_benefits_set and 'movies' in special_perks_lower:
            key_reasons.append("Offers specific benefits for movie tickets.")
        if 'fuel' in user_preferred_benefits_set and 'fuel' in special_perks_lower:
            if "Excellent for fuel savings." not in key_reasons:  # Avoid duplication
                key_reasons.append(
                    "Provides significant savings on fuel expenses.")

        # Ensure unique reasons and add a generic one if no specific reasons found
        key_reasons = list(set(key_reasons))  # Deduplicate reasons
        if not key_reasons:
            key_reasons.append(
                "A strong all-around card based on your overall financial profile.")

        # Calculate net annual benefit (estimated rewards minus total fees)
        net_annual_benefit = estimated_annual_rewards - \
            (card['joining_fee'] + card['annual_fee'])

        # Only include cards with a positive net benefit or those with minimal/no fees
        # Adjusted the fee threshold slightly to allow more cards through if they have decent benefits
        if net_annual_benefit >= 0 or (card['joining_fee'] <= 750 and card['annual_fee'] <= 750):
            ranked_cards.append({
                "card_name": card['name'],
                "image_url": card['image_url'],
                "key_reasons": ", ".join(key_reasons),
                "reward_simulation": f"You could potentially save/earn up to Rs. {net_annual_benefit:,.2f} per year!",
                "net_benefit": net_annual_benefit,  # Used for sorting
                "affiliate_link": card['affiliate_link']
            })

    # --- Deduplicate and Rank Final Recommendations ---
    unique_cards = {}
    for card in ranked_cards:
        card_name = card['card_name']
        if card_name not in unique_cards or card['net_benefit'] > unique_cards[card_name]['net_benefit']:
            unique_cards[card_name] = card

    recommendations = sorted(list(unique_cards.values()),
                             key=lambda x: x['net_benefit'], reverse=True)[:5]

    return recommendations
