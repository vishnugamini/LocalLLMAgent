a = '''Sure! Here’s a simple example of code in Python to add two numbers:

```python
# Function to add two numbers
def add_numbers(num1, num2):
    return num1 + num2

# Input from the user
number1 = float(input("Enter the first number: "))
number2 = float(input("Enter the second number: "))

# Adding the numbers
result = add_numbers(number1, number2)

# Displaying the result
print(f"The sum of {number1} and {number2} is {result}.")
```

You can run this code in a Python environment. It will prompt the user to enter two numbers and then display their sum. Let me know if you need code in a different programming language!'''

start = a.find("```python") + len("```python")
end = a.rfind("```")
code = a[start:end]
print(code)