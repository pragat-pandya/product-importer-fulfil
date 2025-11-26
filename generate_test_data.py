#!/usr/bin/env python3
"""
Generate large test CSV file for FulFil Product Importer
Creates realistic product data with varied categories and attributes
"""
import csv
import random
from datetime import datetime

# Product categories and prefixes
CATEGORIES = {
    'Electronics': ['ELEC', 'TECH', 'GADG'],
    'Furniture': ['FURN', 'HOME', 'DECO'],
    'Clothing': ['CLTH', 'APRL', 'WEAR'],
    'Books': ['BOOK', 'READ', 'LIT'],
    'Sports': ['SPRT', 'FIT', 'OUTD'],
    'Kitchen': ['KTCH', 'COOK', 'UTIL'],
    'Beauty': ['BETY', 'COSM', 'CARE'],
    'Toys': ['TOYS', 'PLAY', 'KIDS'],
    'Tools': ['TOOL', 'HDWR', 'BILD'],
    'Garden': ['GARD', 'PLNT', 'LAWN'],
}

# Product names by category
PRODUCT_NAMES = {
    'Electronics': [
        'Wireless Mouse', 'Bluetooth Keyboard', '4K Monitor', 'USB-C Hub',
        'Laptop Stand', 'Webcam HD', 'Gaming Headset', 'Smart Speaker',
        'Portable Charger', 'Cable Organizer', 'Phone Case', 'Screen Protector',
        'Wireless Earbuds', 'Smart Watch', 'Tablet Stand', 'Desk Lamp LED'
    ],
    'Furniture': [
        'Office Chair', 'Standing Desk', 'Bookshelf', 'Coffee Table',
        'Storage Cabinet', 'Drawer Organizer', 'Wall Shelf', 'Desk Organizer',
        'Filing Cabinet', 'Monitor Stand', 'Coat Rack', 'Shoe Rack',
        'Side Table', 'Ottoman', 'Bench', 'Stool'
    ],
    'Clothing': [
        'T-Shirt Cotton', 'Jeans Denim', 'Hoodie Zip', 'Sneakers Running',
        'Jacket Winter', 'Dress Summer', 'Shorts Casual', 'Socks Athletic',
        'Hat Baseball', 'Gloves Winter', 'Scarf Wool', 'Belt Leather',
        'Sweater Knit', 'Shirt Button-Up', 'Pants Chino', 'Boots Hiking'
    ],
    'Books': [
        'Python Programming Guide', 'JavaScript Essentials', 'Design Patterns',
        'Clean Code', 'Data Structures', 'Machine Learning Basics',
        'Web Development', 'Database Design', 'Algorithms', 'DevOps Handbook',
        'Cloud Computing', 'Cybersecurity Fundamentals', 'UI/UX Design',
        'Project Management', 'Agile Practices', 'System Architecture'
    ],
    'Sports': [
        'Yoga Mat', 'Resistance Bands', 'Dumbbells Set', 'Jump Rope',
        'Exercise Ball', 'Foam Roller', 'Water Bottle', 'Gym Bag',
        'Running Shoes', 'Sports Watch', 'Knee Sleeves', 'Weight Belt',
        'Pull-up Bar', 'Kettlebell', 'Medicine Ball', 'Workout Gloves'
    ],
    'Kitchen': [
        'Knife Set', 'Cutting Board', 'Mixing Bowls', 'Measuring Cups',
        'Spatula Set', 'Pot Set', 'Pan Non-stick', 'Blender', 'Toaster',
        'Coffee Maker', 'Food Processor', 'Can Opener', 'Grater', 'Peeler',
        'Colander', 'Baking Sheet'
    ],
    'Beauty': [
        'Face Cream', 'Moisturizer', 'Shampoo', 'Conditioner', 'Body Lotion',
        'Face Mask', 'Serum Vitamin C', 'Sunscreen SPF 50', 'Lip Balm',
        'Hand Cream', 'Nail Polish', 'Makeup Remover', 'Toner', 'Cleanser',
        'Eye Cream', 'Hair Oil'
    ],
    'Toys': [
        'Building Blocks', 'Puzzle 1000pc', 'Board Game', 'Action Figure',
        'Doll House', 'Remote Control Car', 'Educational Toy', 'Art Set',
        'LEGO Set', 'Stuffed Animal', 'Play Kitchen', 'Train Set',
        'Coloring Book', 'Model Kit', 'Science Kit', 'Musical Toy'
    ],
    'Tools': [
        'Screwdriver Set', 'Hammer', 'Wrench Set', 'Pliers', 'Tape Measure',
        'Level', 'Utility Knife', 'Drill Bits', 'Socket Set', 'Allen Keys',
        'Wire Cutters', 'Flashlight', 'Toolbox', 'Safety Glasses',
        'Work Gloves', 'Voltage Tester'
    ],
    'Garden': [
        'Garden Hose', 'Pruning Shears', 'Rake', 'Shovel', 'Garden Gloves',
        'Plant Pots', 'Watering Can', 'Seeds Vegetable', 'Fertilizer',
        'Soil Mix', 'Garden Kneeler', 'Sprinkler', 'Trowel', 'Garden Fork',
        'Wheelbarrow', 'Hedge Trimmer'
    ],
}

# Descriptive adjectives
ADJECTIVES = [
    'Premium', 'Deluxe', 'Professional', 'Ultra', 'Pro', 'Plus', 'Max',
    'Elite', 'Advanced', 'Classic', 'Modern', 'Essential', 'Standard',
    'Basic', 'Economy', 'Compact', 'Portable', 'Heavy Duty', 'Ergonomic'
]

# Sizes and variants
SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
COLORS = ['Black', 'White', 'Blue', 'Red', 'Green', 'Gray', 'Navy', 'Brown']
MATERIALS = ['Plastic', 'Metal', 'Wood', 'Fabric', 'Leather', 'Aluminum', 'Steel']

def generate_description(category, product_name):
    """Generate a realistic product description"""
    adjective = random.choice(ADJECTIVES)
    
    descriptions = [
        f"{adjective} {product_name} perfect for everyday use. High quality and durable.",
        f"{product_name} with {adjective.lower()} features. Ideal for {category.lower()} enthusiasts.",
        f"Top-rated {product_name.lower()}. {adjective} design with premium materials.",
        f"{adjective} quality {product_name.lower()} designed for comfort and functionality.",
        f"Professional-grade {product_name.lower()}. {adjective} performance guaranteed.",
        f"{product_name} featuring {adjective.lower()} construction. Built to last.",
        f"Stylish {product_name.lower()} with {adjective.lower()} finish. Modern design.",
        f"{adjective} {product_name.lower()} suitable for all skill levels. Great value.",
    ]
    
    return random.choice(descriptions)

def generate_csv(filename='test_products_large.csv', num_products=500):
    """Generate CSV file with test product data"""
    
    print(f"Generating {num_products} test products...")
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['sku', 'name', 'description', 'active']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        products_generated = 0
        
        for i in range(num_products):
            # Select random category
            category = random.choice(list(CATEGORIES.keys()))
            prefix = random.choice(CATEGORIES[category])
            
            # Generate SKU
            sku = f"{prefix}-{i+1:05d}"
            
            # Generate product name
            base_name = random.choice(PRODUCT_NAMES[category])
            
            # Add variant (sometimes)
            name_parts = [base_name]
            if random.random() > 0.6:
                if category == 'Clothing':
                    name_parts.append(random.choice(SIZES))
                    if random.random() > 0.5:
                        name_parts.append(random.choice(COLORS))
                elif random.random() > 0.5:
                    name_parts.insert(0, random.choice(ADJECTIVES))
            
            name = ' '.join(name_parts)
            
            # Generate description
            description = generate_description(category, base_name)
            
            # Random active status (90% active, 10% inactive)
            active = random.random() > 0.1
            
            writer.writerow({
                'sku': sku,
                'name': name,
                'description': description,
                'active': str(active).lower()
            })
            
            products_generated += 1
            
            if (products_generated % 100) == 0:
                print(f"  Generated {products_generated} products...")
    
    print(f"✅ Successfully generated {products_generated} products")
    print(f"📁 File saved: {filename}")
    
    # Calculate file size
    import os
    file_size = os.path.getsize(filename)
    print(f"📊 File size: {file_size / 1024:.2f} KB ({file_size:,} bytes)")

def generate_duplicate_test_csv(filename='test_products_duplicates.csv', num_products=100):
    """Generate CSV with some duplicate SKUs to test upsert functionality"""
    
    print(f"\nGenerating {num_products} products with duplicates...")
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['sku', 'name', 'description', 'active']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        # Generate base products
        base_skus = []
        for i in range(num_products):
            category = random.choice(list(CATEGORIES.keys()))
            prefix = random.choice(CATEGORIES[category])
            sku = f"{prefix}-DUP-{i+1:04d}"
            base_skus.append((sku, category, prefix))
            
            base_name = random.choice(PRODUCT_NAMES[category])
            name = f"{base_name} Original"
            description = f"Original version - {generate_description(category, base_name)}"
            
            writer.writerow({
                'sku': sku,
                'name': name,
                'description': description,
                'active': 'true'
            })
        
        # Add some duplicates (20% of products)
        num_duplicates = int(num_products * 0.2)
        for i in range(num_duplicates):
            sku, category, prefix = random.choice(base_skus)
            base_name = random.choice(PRODUCT_NAMES[category])
            name = f"{base_name} Updated"
            description = f"UPDATED version - {generate_description(category, base_name)}"
            
            writer.writerow({
                'sku': sku,  # Duplicate SKU
                'name': name,
                'description': description,
                'active': random.choice(['true', 'false'])
            })
    
    print(f"✅ Generated {num_products} base products + {num_duplicates} duplicates")
    print(f"📁 File saved: {filename}")

if __name__ == '__main__':
    import sys
    
    # Parse command line arguments
    num_products = 500
    if len(sys.argv) > 1:
        try:
            num_products = int(sys.argv[1])
        except ValueError:
            print(f"Invalid number: {sys.argv[1]}, using default: 500")
    
    print("=" * 60)
    print("FulFil Test Data Generator")
    print("=" * 60)
    print()
    
    # Generate main test file
    generate_csv('test_products_large.csv', num_products)
    
    # Generate duplicate test file
    generate_duplicate_test_csv('test_products_duplicates.csv', 100)
    
    print()
    print("=" * 60)
    print("✅ Test files generated successfully!")
    print()
    print("Files created:")
    print("  1. test_products_large.csv - Large dataset for bulk import testing")
    print("  2. test_products_duplicates.csv - Dataset with duplicates for upsert testing")
    print()
    print("Usage:")
    print("  Upload test_products_large.csv to test bulk import and pagination")
    print("  Upload test_products_duplicates.csv twice to test upsert functionality")
    print("=" * 60)

