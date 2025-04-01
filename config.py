# Path configuration
INPUT_DIR = "/home/tejus09/Desktop/PersonAttr/unpadded_data"
OUTPUT_DIR = "/home/tejus09/Desktop/PersonAttr/verified_data"

# Create output directory if it doesn't exist
import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Attribute validation lists
VEHICLE_BRANDS = ["TVS", "Maruti-Suzuki", "Eicher", "Ashok_leyland", "Mercedes-Benz",
                 "Royal_Enfield", "Chevrolet", "Fiat", "Jaguar", "Audi", "Toyota", 
                 "SML", "Bajaj", "JBM", "Bharat_Benz", "Hero_Motor", "Volvo", 
                 "Nissan", "Renault", "Volkswagen", "Mazda", "Hero-Honda", "Hyundai", 
                 "MG", "Skoda", "Land_Rover", "Yamaha", "Kia", "Mahindra", 
                 "Mitsubishi", "Ford", "Jeep", "Tata-Motors", "Honda", "BMW", 
                 "Coupe", "Force", "None of the above"]

VEHICLE_COLORS = ["Khakhi", "Silver", "Yellow", "Pink", "Purple", "Green", "Blue", 
                 "Brown", "Maroon", "Red", "Orange", "Violet", "White", "Black", "Gray", "None of the above"]

VEHICLE_ORIENTATIONS = ["Front", "Back", "Side", "None of the above"]

VEHICLE_LABELS = ["Bus", "Car", "Truck", "Motorbike", "Bicycle", "E-Rikshaw", 
                 "Cycle_Rikshaw", "Tractor", "Cement_Mixer", "Mini_Truck", 
                 "Mini_Bus", "Mini_Van", "Van", "None of the above"]

VEHICLE_ITYPES = ["HMV", "LMV", "LGV", "3-Axle", "5-Axle", "MGWG", "6-Axle", 
                 "2-Axle", "4-Axle", "Heavy-Vehicle", "None of the above"]

VEHICLE_TYPES = ["Sedan", "SUV", "Micro", "Hatchback", "Wagon", "Pick-Up", "Convertible", "None of the above"]

VEHICLE_SPECIAL_TYPES = ["Army_Vehicle", "Ambulance", "Graminseva_4wheeler", 
                        "Graminseva_3wheeler", "Campervan", "None of the above"]

# Progress tracking
PROGRESS_FILE = os.path.join(OUTPUT_DIR, "verification_progress.json") 