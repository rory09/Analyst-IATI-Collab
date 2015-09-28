import xml.etree.ElementTree as ET
import requests
import sys

# Canada, WFP, Unicef

'''README: to use this script, you must include 2 or more arguments when calling it. The first must be the IATI identifier of the Organisation
you wish to examine, and then one or more country codes afterwards. For each country code provided, a row will be appended into the csv terminal output.'''

org = sys.argv[1]
start = '2015-01-01'

# Print the header for csv output
print("org, country, start, number_of_activities, activities_without_budgets, percent, total_budgets, budget_collisions, response.url")

# Repeat this process for every country given
for i in range(2,len(sys.argv)):

	# The following lines translate the user provided arguments into an html api call for the IATI registry, download an xml response,
	# and then parse it into memory
	country = sys.argv[i]
	payload = {'reporting-org': org, 'recipient-country': country, 'end-date__gt': start, 'stream':'True'}
	response = requests.get("http://datastore.iatistandard.org/api/1/access/activity.xml", params=payload)
	result = ET.fromstring(response.content)
	activities = result.findall("./iati-activities/iati-activity")

	# Set our initial values
	number_of_activities = 0
	activities_without_budgets = 0
	total_committed = 0
	total_budgets = 0
	budget_collisions = 0

	# For each activity
	for activity in activities:
		
		# counter for the budget collisions found in this activity
		current_budget_collisions = 0

		# count total number of activities
		number_of_activities += 1

		# Extract budget elements and print how many there are
		budget_elements = activity.findall("budget")
		
		# Are there budget elements?
		if len(budget_elements) > 0:
			
			# Store the number of budgets
			total_budgets += len(budget_elements)

			# Create a budget dictionary so that we can compare revised / non-revised budgets and insert the approapriate one
			found_budgets = {}
			for budget in budget_elements:
				for child in budget:
					# look at the budgets start and end dates to make sure that it's unique
					date_string = ""
					if child.tag != 'value':
						date_string = date_string + child.attrib['iso-date']
					
						if date_string not in found_budgets.keys():
							found_budgets[date_string] = 1 
						else:	current_budget_collisions += 1

			# add the budget collisions to the total
			budget_collisions += current_budget_collisions
		
		else:
			activities_without_budgets += 1	
					
	# Output the total, activities_without_budgets
	percent = float(number_of_activities - activities_without_budgets) / float(number_of_activities) * 100
	print "%s,%s,%s,%i,%i,%f,%i,%i,%s" % (org, country, start, number_of_activities, activities_without_budgets, percent, total_budgets, budget_collisions, response.url)
