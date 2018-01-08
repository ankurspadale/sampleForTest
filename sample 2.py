"""
@wi EL-137 EL-137 main module comment
This is a multiline comment for the document. This docstring comment describes requirements for our python parser.

- The format of a single requirement claim shall be the following: Req LSA-\d+
- The format of multiple requirement claims shall be the following: Req LSA-\d+ LSA-\d+ LSA-\d+ LSA-\d+ ...
-- Example: Req LSA-0001 LSA-0002 LSA-0003

- The parser shall support tracing to entire files.
-- All instances of the requirement format found in a file-level docstring shall trace that file to that requirement.

- The parser shall support tracing to functions.
-- All instances of the requirement format found in a function-level docstring shall trace the requirement to that function and file

- The parser shall support tracing to lines.
-- All instances of the requirement format found in a line-level comment shall trace the requirement to that line and file


The following line is an example of a claim to this file

@wi LSA-1234

"""

class MyClass:
	"""@wi EL-137 MyClass DocString comment """
    # @wi EL-137 MyClass 2nd comment
	a = 10
    # @wi EL-137 MyClass 3nd comment
	def myFunc(self):
        # @wi EL-137 myFunc DocString comment
        # asda decode
        # @wi EL-137 myFunc 2nd comment
		print('Hello')

def myFunc2(self):
    # @wi EL-139 myFunc2 DocString comment
    print('Hello')

"""asdasdas"""
    
# extra middle comment
print(MyClass.a)

# @wi EL-137 random statement comment
print(MyClass.func)


# extra last comment
print(MyClass.__doc__)

#
class sample: