import json

with open("out_files/json/institutes_all.json") as data:
    inst_data=json.load(data)

# print(inst_data.keys())
colleges = inst_data.keys()

# print(inst_data["Humber College"].get('hostel_fee'))
for college in colleges:
    try:
        hostel_fee = inst_data[college]['hostel_fee']
        if hostel_fee is float:
            hostel_fee = str(int(float(hostel_fee)*100000))
            print(college, hostel_fee, end='\t')
            inst_data[college]['hostel_fee'] = hostel_fee
        else:
            print("already modified", college, hostel_fee)
    except ValueError:
        continue

# with open("out_files/json/institutes_all.json", "w") as data:
#     json.dump(inst_data, data, indent=2)
