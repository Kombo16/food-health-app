""" Food categorization utility """

class FoodCategorizer:
    """ Utility class for categorizing food items based on predefined categories """

    def __init__(self, food_categories):
        self.category_keywords = {
            'fruits': ['apple', 'banana', 'orange', 'berry', 'grape', 'fruit', 'citrus', 'mango', 'pineapple'],
            'vegetables': ['broccoli', 'spinach', 'carrot', 'lettuce', 'tomato', 'pepper', 'onion'],
            'grains': ['bread', 'rice', 'pasta', 'cereal', 'wheat', 'oat', 'quinoa', 'barley'],
            'proteins': ['chicken', 'beef', 'fish', 'egg', 'meat', 'pork', 'turkey', 'salmon', 'tuna'],
            'dairy': ['milk', 'cheese', 'yogurt', 'cream', 'butter', 'cottage cheese'],
            'snacks': ['chips', 'crackers', 'nuts', 'seeds', 'popcorn', 'chocolate', 'candy']
        }

    def categorize(self, food_description: str) -> str:
        """ Categorize a food item based on its description """
        description = food_description.lower()
        for category, keywords in self.category_keywords.items():
            if any(keyword in description for keyword in keywords):
                return category
        # If no category matches, return 'unknown'
        if 'unknown' in self.category_keywords:
            return 'unknown'