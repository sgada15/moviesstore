REGIONS = {
    'north_america': {'name': 'North America', 'lat': 45.0, 'lng': -100.0},
    'south_america': {'name': 'South America', 'lat': -15.0, 'lng': -60.0},
    'europe': {'name': 'Europe', 'lat': 50.0, 'lng': 10.0},
    'africa': {'name': 'Africa', 'lat': 2.0, 'lng': 20.0},
    'asia': {'name': 'Asia', 'lat': 35.0, 'lng': 100.0},
    'oceania': {'name': 'Oceania', 'lat': -25.0, 'lng': 135.0},
}

REGION_CHOICES = [(key, value['name']) for key, value in REGIONS.items()]
