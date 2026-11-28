from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from planner.models import Event, Profile, Shift, Zone


class Command(BaseCommand):
    help = "Create sample future events and open volunteer shifts."

    @transaction.atomic
    def handle(self, *args, **options):
        organizer, created = User.objects.get_or_create(
            username="volunteerconnect-demo-organizer",
            defaults={"email": "", "is_active": True},
        )
        if created:
            organizer.set_unusable_password()
            organizer.save(update_fields=["password"])
        Profile.objects.get_or_create(
            user=organizer,
            defaults={"role": "ORGANIZER", "organization": "VolunteerConnect Demo"},
        )

        opportunities = [
            {
                "event": "Community Food Drive",
                "venue": "Central Community Hall",
                "description": "Help distribute groceries and essentials to local families.",
                "day": 3,
                "shifts": [
                    ("Food Sorting", "Sort donated food into family-sized packages.", "Food Distribution", 12),
                    ("Guest Welcome Desk", "Welcome visitors and help them find the right supplies.", "Guest Welcome", 4),
                ],
            },
            {
                "event": "Neighborhood Clean-Up",
                "venue": "Riverside Park",
                "description": "Join neighbors to care for shared paths and green spaces.",
                "day": 5,
                "shifts": [
                    ("Park Path Clean-Up", "Collect litter and help keep park paths safe and tidy.", "Park Restoration", 10),
                    ("Volunteer Check-In", "Check in volunteers and hand out clean-up supplies.", "Supply Check-in", 3),
                ],
            },
            {
                "event": "Community Garden Day",
                "venue": "Maple Street Community Garden",
                "description": "Help prepare garden beds and care for this neighborhood growing space.",
                "day": 8,
                "shifts": [
                    ("Garden Bed Preparation", "Prepare planting beds and tidy the garden area.", "Garden Crew", 8),
                    ("Compost and Watering Team", "Turn compost and water established garden beds.", "Compost & Water", 5),
                ],
            },
            {
                "event": "Neighborhood Blood Drive",
                "venue": "Eastside Health Center",
                "description": "Support a local blood donation drive and help donors feel welcome.",
                "day": 11,
                "shifts": [
                    ("Donor Welcome Team", "Greet donors and guide them through check-in.", "Donor Check-in", 5),
                    ("Refreshment Station", "Prepare refreshments for donors after their appointments.", "Donor Care", 4),
                ],
            },
            {
                "event": "Animal Shelter Volunteer Day",
                "venue": "Happy Tails Animal Shelter",
                "description": "Help the shelter care for animals and connect with prospective adopters.",
                "day": 14,
                "shifts": [
                    ("Shelter Enrichment Helpers", "Prepare toys and enrichment activities for shelter animals.", "Animal Enrichment", 6),
                    ("Adoption Day Greeters", "Welcome visitors and help them find the adoption area.", "Adoption Welcome", 4),
                ],
            },
            {
                "event": "Community Literacy Fair",
                "venue": "Westside Public Library",
                "description": "Help celebrate reading and connect families with local literacy resources.",
                "day": 17,
                "shifts": [
                    ("Book Fair Setup Crew", "Set up tables and organize books before the fair opens.", "Fair Setup", 8),
                    ("Reading Corner Volunteers", "Welcome young readers and help with story activities.", "Reading Corner", 5),
                ],
            },
            {
                "event": "City Park Tree Planting",
                "venue": "Oakwood City Park",
                "description": "Plant native trees and help improve shade and habitat in the park.",
                "day": 20,
                "shifts": [
                    ("Tree Planting Crew", "Plant and stake young native trees.", "Planting Area", 10),
                    ("Tools and Supplies", "Prepare, organize, and return planting tools.", "Tool Station", 4),
                    ("Watering Team", "Water newly planted trees and refill water containers.", "Watering Point", 6),
                    ("Volunteer Check-In", "Welcome volunteers and share planting instructions.", "Park Check-in", 3),
                ],
            },
            {
                "event": "Senior Center Social",
                "venue": "Sunrise Senior Center",
                "description": "Spend time with local seniors and help host a welcoming community gathering.",
                "day": 23,
                "shifts": [
                    ("Activities Helpers", "Set up and assist with group games and activities.", "Activities Room", 5),
                    ("Tea and Refreshments", "Serve refreshments and keep the social area tidy.", "Refreshment Table", 4),
                    ("Guest Companions", "Chat with guests and help them get settled.", "Lounge", 6),
                    ("Event Setup Crew", "Arrange seating and prepare the gathering space.", "Main Hall", 4),
                ],
            },
            {
                "event": "Riverside Recycling Day",
                "venue": "Riverside Community Center",
                "description": "Help residents recycle household items and learn about waste reduction.",
                "day": 26,
                "shifts": [
                    ("Recycling Sorters", "Sort accepted materials at the collection area.", "Sorting Station", 8),
                    ("Resident Guides", "Direct visitors to the correct drop-off points.", "Welcome Lane", 5),
                    ("Weigh-In Assistants", "Record the weights of collected recyclable materials.", "Weighing Point", 3),
                    ("Site Clean-Up Crew", "Keep collection lanes clear and tidy throughout the event.", "Site Support", 5),
                ],
            },
            {
                "event": "School Supply Collection",
                "venue": "Northside Learning Hub",
                "description": "Collect and organize school supplies for students and local classrooms.",
                "day": 29,
                "shifts": [
                    ("Supply Donation Sorters", "Sort donated notebooks, stationery, and backpacks.", "Sorting Room", 7),
                    ("Packing Team", "Pack supplies into classroom-ready kits.", "Packing Tables", 8),
                    ("Donation Welcome Desk", "Greet donors and direct them to drop-off.", "Donation Entrance", 3),
                    ("Inventory Helpers", "Count and label prepared supply kits.", "Inventory Desk", 4),
                ],
            },
            {
                "event": "Local Food Bank Packing Day",
                "venue": "Greenway Food Bank",
                "description": "Pack food parcels and support the food bank's distribution operations.",
                "day": 32,
                "shifts": [
                    ("Parcel Packing Team", "Assemble food parcels using the packing checklist.", "Packing Line", 12),
                    ("Fresh Produce Sorters", "Check and sort fresh produce for distribution.", "Produce Area", 6),
                    ("Loading Area Assistants", "Prepare packed parcels for pickup and delivery.", "Loading Bay", 5),
                    ("Visitor Welcome Desk", "Welcome food bank visitors and answer basic questions.", "Reception", 3),
                ],
            },
            {
                "event": "Community Arts Festival",
                "venue": "Millstone Arts Plaza",
                "description": "Help local artists and families enjoy a day of creative activities.",
                "day": 35,
                "shifts": [
                    ("Workshop Assistants", "Help artists prepare materials for hands-on workshops.", "Workshop Tent", 6),
                    ("Festival Information Desk", "Share the schedule and help visitors navigate the festival.", "Information Booth", 4),
                    ("Kids' Art Corner Helpers", "Support children's art activities and tidy materials.", "Family Art Zone", 5),
                    ("Stage Area Crew", "Help prepare seating and keep the performance area organized.", "Performance Stage", 4),
                ],
            },
            {
                "event": "Coastal Habitat Restoration",
                "venue": "Seabreeze Nature Reserve",
                "description": "Support habitat restoration and care for native coastal plants.",
                "day": 38,
                "shifts": [
                    ("Native Planting Team", "Plant native seedlings in prepared restoration areas.", "North Habitat", 8),
                    ("Trail Care Crew", "Clear light debris from designated public trails.", "Trail Entrance", 6),
                    ("Nature Walk Guides", "Help visitors follow the marked restoration route.", "Visitor Trail", 4),
                    ("Field Supplies Station", "Organize gloves, tools, and water for volunteers.", "Field Station", 3),
                ],
            },
            {
                "event": "Neighborhood Health Fair",
                "venue": "Central Wellness Pavilion",
                "description": "Help connect neighbors with health information and community resources.",
                "day": 41,
                "shifts": [
                    ("Health Fair Greeters", "Welcome visitors and help them find the registration area.", "Main Entrance", 5),
                    ("Resource Table Helpers", "Keep community information and resource tables organized.", "Resource Hall", 4),
                    ("Activity Area Assistants", "Support family activities and manage supplies.", "Activity Room", 6),
                    ("Visitor Flow Guides", "Help visitors navigate between fair stations.", "Pavilion Walkway", 5),
                ],
            },
        ]

        now = timezone.now()
        created_shifts = 0
        total_shifts = sum(len(opportunity["shifts"]) for opportunity in opportunities)
        for opportunity in opportunities:
            event_start = (now + timedelta(days=opportunity["day"])).replace(
                hour=9, minute=0, second=0, microsecond=0
            )
            event, _ = Event.objects.update_or_create(
                title=opportunity["event"],
                venue=opportunity["venue"],
                defaults={
                    "description": opportunity["description"],
                    "starts_at": event_start,
                    "ends_at": event_start + timedelta(hours=8),
                    "published": True,
                    "created_by": organizer,
                },
            )
            for index, (title, description, zone_name, capacity) in enumerate(opportunity["shifts"]):
                zone, _ = Zone.objects.get_or_create(
                    name=zone_name,
                    defaults={"location": opportunity["venue"]},
                )
                shift_start = event_start + timedelta(hours=index * 2)
                _, shift_created = Shift.objects.update_or_create(
                    event=event,
                    zone=zone,
                    title=title,
                    defaults={
                        "description": description,
                        "starts_at": shift_start,
                        "ends_at": shift_start + timedelta(hours=2),
                        "capacity": capacity,
                        "status": "OPEN",
                    },
                )
                created_shifts += int(shift_created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo data is ready: {len(opportunities)} events and "
                f"{total_shifts} open shifts "
                f"({created_shifts} shifts newly created)."
            )
        )
