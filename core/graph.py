import re
import math

def generate_indices(complexity: str, num_inputs: int):
    # Remove the "O(" and ")" to extract the mathematical function
    complexity = complexity[2:-1]
    
    loop_broke = False
    x_values = range(1, num_inputs + 1, 100)
    
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
        indices.append((x, min(value, 10**4299 - 1)))
        # Break the loop if value exceeds 100,000
        if value > 1000000000000:
            loop_broke = True
            break
    
    # If loop broke due to high value, recalculate with smaller range
    if loop_broke:
        indices.clear()
        x_values = range(1, 10)  # New range from 1 to 100 with step size 1
        
        for x in x_values:            
            # Handle special cases like log, factorial, powers, etc.
            expression = complexity.replace('n', str(x))
            if 'log' in expression:
                value = eval(expression.replace('log', 'math.log'))
            elif '!' in expression:
                value = math.factorial(x)
            else:
                # General case for powers and other expressions
                expression = expression.replace('^', '**')  # Convert '^' to Python's '**'
                value = eval(expression)
            
            # Add the index (x, value) to the result list
            indices.append((x, min(value, 10**4299 - 1)))
    
    return indices