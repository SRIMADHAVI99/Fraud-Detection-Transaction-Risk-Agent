import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

LOCATIONS = ['Hyderabad', 'Mumbai', 'Bangalore', 'Delhi', 'Pune', 'Chennai', 'Kolkata', 'Singapore', 'Dubai', 'London', 'New York']
DEVICES = ['iPhone 15', 'Samsung S24', 'Chrome Windows', 'Safari macOS', 'Android Device', 'Unknown Web Client']
PAYMENT_METHODS = ['Credit Card', 'UPI', 'Net Banking', 'Debit Card']

def generate_transactions(num_records=15000, seed=42):
    np.random.seed(seed)
    random.seed(seed)
    
    records = []
    end_time = datetime.now()
    start_time = end_time - timedelta(days=30)
    time_step_seconds = (30 * 86400) / num_records
    
    for i in range(1, num_records + 1):
        txn_id = f"TXN{10000 + i}"
        is_fraud = 1 if random.random() < 0.10 else 0
        user_avg = float(random.choice([1500, 2500, 3500, 5000, 8000, 12000]))
        
        if is_fraud == 0:
            if random.random() < 0.95:
                hour = random.randint(7, 22)
            else:
                hour = random.choice([23, 0, 1, 2, 3, 4, 5, 6])
                
            new_device = 1 if random.random() < 0.05 else 0
            location_change = 1 if random.random() < 0.08 else 0
            txns_10m = random.choice([1, 1, 1, 1, 1, 2, 2, 3])
            
            ratio = np.random.lognormal(mean=0.0, sigma=0.4)
            ratio = np.clip(ratio, 0.2, 3.0)
            
            if random.random() < 0.03:
                ratio = random.uniform(3.5, 7.0)
                new_device = 0
                location_change = 0
                txns_10m = 1
                
            amount = user_avg * ratio
            location = random.choice(LOCATIONS[:5]) if location_change == 0 else random.choice(LOCATIONS[5:])
            device = random.choice(DEVICES[:4]) if new_device == 0 else random.choice(DEVICES[4:])

        else:
            typology = random.choice(['ATO', 'VELOCITY_MICRO', 'GEO_JUMP_NIGHT', 'NIGHT_SPIKE', 'CARD_TEST_DRAIN'])
            
            if typology == 'ATO':
                new_device = 1
                location_change = 1
                hour = random.randint(0, 23)
                txns_10m = random.randint(1, 4)
                ratio = random.uniform(3.5, 10.0)
                
            elif typology == 'VELOCITY_MICRO':
                new_device = random.choice([0, 1])
                location_change = random.choice([0, 1])
                hour = random.randint(0, 23)
                txns_10m = random.randint(5, 15)
                ratio = random.uniform(0.1, 1.5)
                
            elif typology == 'GEO_JUMP_NIGHT':
                new_device = 1
                location_change = 1
                hour = random.choice([0, 1, 2, 3, 4, 5, 23])
                txns_10m = random.randint(4, 9)
                ratio = random.uniform(2.0, 6.0)
                
            elif typology == 'NIGHT_SPIKE':
                new_device = random.choice([0, 1])
                location_change = random.choice([0, 1])
                hour = random.choice([1, 2, 3, 4])
                txns_10m = random.randint(1, 3)
                ratio = random.uniform(5.0, 12.0)
                
            else:
                new_device = 1
                location_change = random.choice([0, 1])
                hour = random.randint(0, 23)
                txns_10m = random.randint(6, 12)
                ratio = random.uniform(4.0, 9.0)
                
            amount = user_avg * ratio
            location = random.choice(LOCATIONS[4:]) if location_change == 1 else random.choice(LOCATIONS[:4])
            device = random.choice(DEVICES[4:]) if new_device == 1 else random.choice(DEVICES[:4])

        amount = round(float(amount), 2)
        amount_ratio = round(float(amount / user_avg), 2)
        
        # Calculate timestamp evenly leading up to datetime.now()
        timestamp = start_time + timedelta(seconds=i * time_step_seconds)
        timestamp = timestamp.replace(hour=hour, minute=random.randint(0, 59), second=random.randint(0, 59))
        
        records.append({
            'transaction_id': txn_id,
            'amount': amount,
            'location': location,
            'device': device,
            'payment_method': random.choice(PAYMENT_METHODS),
            'hour': hour,
            'avg_amount': user_avg,
            'amount_ratio': amount_ratio,
            'new_device': new_device,
            'location_change': location_change,
            'transactions_last_10min': txns_10m,
            'is_fraud': is_fraud,
            'created_at': timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    df = pd.DataFrame(records)
    
    df.to_csv(DATA_DIR / 'transactions.csv', index=False)
    df.head(100).to_csv(DATA_DIR / 'sample_transactions.csv', index=False)
    
    print(f"Generated {len(df)} transactions ending at {end_time.strftime('%Y-%m-%d %H:%M:%S')}.")
    return df

if __name__ == '__main__':
    generate_transactions()
