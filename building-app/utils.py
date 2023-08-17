""" utility functions to extract from product module """

import openai
from products import products

# help functions
def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0, max_tokens=500):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, 
        max_tokens=max_tokens, 
    )
    return response.choices[0].message["content"]

# extract catetory and product from product detailed info
# because the detailed info beyond gpt model's max tokens
# "InvalidRequestError: This model's maximum context length is 4097 tokens. However, your messages resulted in 6164 tokens. Please reduce the length of the messages."
def extract_category_and_product():
    delimiter = "####"
    system_message = f"""
    You will be provided with product details. \
    The product details will be delimited with \
    {delimiter} characters.
    Output a json summary with the following format:\
        <a category name> : <list of all product names that belong to the catetory>
        
    Where the categories and products must be found in \
    the product details.
    If no products or categories are found, output an \
    empty list.

    Only output the list of objects, with nothing else.
    """
    messages =  [  
    {'role':'system', 'content': system_message},    
    {'role':'user', 'content': f"{delimiter}{products.values()}{delimiter}"},  
    ] 
    products_and_category_found = get_completion_from_messages(messages)
    return products_and_category_found

# get_products_and_category
def get_products_and_category(user_input, category_and_product_list):
    delimiter = "####"
    system_message = f"""
    You will be provided with customer service queries. \
    The customer service query will be delimited with \
    {delimiter} characters.
    
    Output a python list of objects, where each object has \
    the following format:
        'category': <a category in the allowed products below>,
    OR
        'products': <a list of products that must be found in the allowed products below>
    
    Where the categories and products must be found in \
    the customer service query.
    If a product is mentioned, it must be associated with \
    the correct category in the allowed products below
    If no products or categories are found, output an \
    empty list.

    allowed products:
    {category_and_product_list}

    Only output the list of objects, with nothing else.
    """
    messages =  [  
    {'role':'system', 'content': system_message},    
    {'role':'user', 'content': f"{delimiter}{user_input}{delimiter}"},  
    ] 
    products_and_category_response = get_completion_from_messages(messages)
    return products_and_category_response


# read_string_to_list
import json 

def read_string_to_list(input_string):
    if input_string is None:
        return None

    try:
        input_string = input_string.replace("'", "\"")  # Replace single quotes with double quotes for valid JSON
        data = json.loads(input_string)
        return data
    except json.JSONDecodeError:
        print("Error: Invalid JSON string")
        return None  


# generate_output_string
def get_product_by_name(name):
    return products.get(name, None)

def get_products_by_category(category):
    return [product for product in products.values() if product["category"] == category]
    
def generate_output_string(data_list):
    output_string = ""

    if data_list is None:
        return output_string

    for data in data_list:
        try:
            if "products" in data:
                products_list = data["products"]
                for product_name in products_list:
                    product = get_product_by_name(product_name)
                    if product:
                        output_string += json.dumps(product, indent=4) + "\n"
                    else:
                        print(f"Error: Product '{product_name}' not found")
            elif "category" in data:
                category_name = data["category"]
                category_products = get_products_by_category(category_name)
                for product in category_products:
                    output_string += json.dumps(product, indent=4) + "\n"
            else:
                print("Error: Invalid object format")
        except Exception as e:
            print(f"Error: {e}")

    return output_string 