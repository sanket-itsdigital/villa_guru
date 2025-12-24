# Generated manually to handle data migration from hotel to villa

from django.db import migrations


def migrate_hotel_to_villa_data(apps, schema_editor):
    """Copy data from old hotel tables to new villa tables"""
    # Get old models
    OldHotel = apps.get_model('hotel', 'hotel')
    OldHotelRooms = apps.get_model('hotel', 'hotel_rooms')
    OldHotelImage = apps.get_model('hotel', 'HotelImage')
    OldHotelRoomsImage = apps.get_model('hotel', 'hotel_roomsImage')
    OldHotelAvailability = apps.get_model('hotel', 'HotelAvailability')
    OldRoomAvailability = apps.get_model('hotel', 'RoomAvailability')
    
    # Get new models
    Villa = apps.get_model('hotel', 'villa')
    VillaRooms = apps.get_model('hotel', 'villa_rooms')
    VillaImage = apps.get_model('hotel', 'VillaImage')
    VillaRoomsImage = apps.get_model('hotel', 'villa_roomsImage')
    VillaAvailability = apps.get_model('hotel', 'VillaAvailability')
    
    # Create a mapping of old hotel IDs to new villa IDs
    hotel_to_villa_map = {}
    
    # Migrate hotels to villas
    for old_hotel in OldHotel.objects.all():
        new_villa = Villa.objects.create(
            villa_id=old_hotel.hotel_id,
            name=old_hotel.name,
            category=old_hotel.category,
            no_of_rooms=old_hotel.no_of_rooms,
            address=old_hotel.address,
            landmark=old_hotel.landmark,
            pincode=old_hotel.pincode,
            star_rating=old_hotel.star_rating,
            overall_rating=old_hotel.overall_rating,
            main_image=old_hotel.main_image,
            profit_margin=old_hotel.profit_margin,
            is_featured=old_hotel.is_featured,
            is_recommended=old_hotel.is_recommended,
            description=old_hotel.description,
            is_active=old_hotel.is_active,
            go_live=old_hotel.go_live,
            price_per_night=old_hotel.price_per_night,
            created_at=old_hotel.created_at,
            gst_number=old_hotel.gst_number,
            gst_certificate=old_hotel.gst_certificate,
            pan_number=old_hotel.pan_number,
            account_holder_name=old_hotel.account_holder_name,
            account_number=old_hotel.account_number,
            ifsc_code=old_hotel.ifsc_code,
            bank_name=old_hotel.bank_name,
            bank_document=old_hotel.bank_document,
            user=old_hotel.user,
            city=old_hotel.city,
            property_type=old_hotel.property_type,
        )
        # Copy many-to-many relationships
        new_villa.amenities.set(old_hotel.amenities.all())
        hotel_to_villa_map[old_hotel.id] = new_villa
        
        # Migrate hotel images
        for old_image in OldHotelImage.objects.filter(hotel=old_hotel):
            VillaImage.objects.create(
                villa=new_villa,
                image=old_image.image,
            )
        
        # Migrate hotel availability
        for old_avail in OldHotelAvailability.objects.filter(hotel=old_hotel):
            VillaAvailability.objects.create(
                villa=new_villa,
                date=old_avail.date,
                is_open=old_avail.is_open,
            )
    
    # Create a mapping of old room IDs to new room IDs
    room_to_villa_room_map = {}
    
    # Migrate hotel rooms to villa rooms
    for old_room in OldHotelRooms.objects.all():
        old_hotel_id = old_room.hotel.id if old_room.hotel else None
        new_villa = hotel_to_villa_map.get(old_hotel_id) if old_hotel_id else None
        
        new_room = VillaRooms.objects.create(
            villa=new_villa,
            room_type=old_room.room_type,
            main_image=old_room.main_image,
            max_guest_count=old_room.max_guest_count,
            title=old_room.title,
            description=old_room.description,
            price_per_night=old_room.price_per_night,
            refundable=old_room.refundable,
            meals_included=old_room.meals_included,
            bed_type=old_room.bed_type,
            capacity=old_room.capacity,
            view=old_room.view,
        )
        # Copy many-to-many relationships
        new_room.room_amenities.set(old_room.room_amenities.all())
        room_to_villa_room_map[old_room.id] = new_room
        
        # Migrate room images
        for old_image in OldHotelRoomsImage.objects.filter(hotel_rooms=old_room):
            VillaRoomsImage.objects.create(
                villa_rooms=new_room,
                image=old_image.image,
            )
    
    # Update RoomAvailability to point to new villa_rooms
    # We need to use raw SQL to update the foreign key
    RoomAvailability = apps.get_model('hotel', 'RoomAvailability')
    for old_room_avail in OldRoomAvailability.objects.all():
        old_room_id = old_room_avail.room.id
        new_room = room_to_villa_room_map.get(old_room_id)
        if new_room:
            # Update the foreign key directly in the database
            with schema_editor.connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE hotel_roomavailability SET room_id = %s WHERE id = %s",
                    [new_room.id, old_room_avail.id]
                )


def reverse_migration(apps, schema_editor):
    """Reverse migration - not implemented as it's complex"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0031_hotel_price_per_night'),
        ('customer', '0024_villabooking_alter_favouritehotel_unique_together_and_more'),
    ]

    operations = [
        migrations.RunPython(migrate_hotel_to_villa_data, reverse_migration),
    ]

