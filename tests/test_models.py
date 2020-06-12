

# Should pull an existing track with that ID from the database
existing_track = Track(id="foo")

new_track = Track(round_number=3)
new_track.person = "Toph Allen"
new_track.insert()