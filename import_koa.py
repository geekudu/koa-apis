import csv
from users.models import Member

with open('koa.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        Member.objects.create(
            name=row[1],
            email=row[10],
            KOALM_number=row[0],
            address=row[3]+ " " + row[4],
            communication_address=row[2],
            district=row[5],
            pincode=row[6],
            state=row[7],
            district_club_name=row[8],
            mobile_number=row[9],
        )
        print(f"Member {row[0]} created successfully")