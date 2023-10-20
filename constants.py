from math import cos, sin, asin, sqrt


# Function for defining the custom distance metric (Haversine distance, in this case)
def haversine(point1, point2):
    lat1, lon1 = point1[0], point1[1]
    lat2, lon2 = point2[0], point2[1]
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r
