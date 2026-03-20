import csv
from users.models import Member

with open('koa2.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        member, created = Member.objects.get_or_create(KOALM_number=row[0])
        # if created:
        member.name = row[1]
        member.email = row[10]
        member.address = row[3]+ " " + row[4]
        member.communication_address = row[2]
        member.district = row[5]
        member.pincode = row[6]
        member.state = row[7]
        member.district_club_name = row[8]
        member.mobile_number = row[9]
        member.save()
        print(f"Member {row[0]} created successfully")