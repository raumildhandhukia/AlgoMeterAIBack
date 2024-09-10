import re
import math

def generate_indices(complexity: str, num_inputs: int):
    # Remove the "O(" and ")" to extract the mathematical function
    complexity = re.sub(r'O\(|\)', '', complexity)
    
    # Create a range of input sizes
    x_values = range(1, num_inputs + 1, 10000)
    
    # Handle common complexities
    indices = []
    for x in x_values:
        # Replace 'n' with the input value in the complexity string
        expression = complexity.replace('n', str(x))
        
        # Handle special cases like log, factorial, powers, etc.
        if 'log' in expression:
            value = eval(expression.replace('log', 'math.log'))
        elif '!' in expression:
            value = math.factorial(x)
        else:
            # General case for powers and other expressions
            expression = expression.replace('^', '**')  # Convert '^' to Python's '**'
            value = eval(expression)
        
        # Add the index (x, value) to the result list
        indices.append((x, value))
    
    return indices