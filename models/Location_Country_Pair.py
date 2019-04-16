class LocationCountryPair:

    def __init__(self, location_name, country_name):
        self.location_name = location_name
        self.country_name = country_name

    def __hash__(self):
        return hash((self.location_name, self.country_name))

    def __eq__(self, other):
        return (self.location_name, self.country_name) == (other.location_name, other.country_name)

    def get_location(self):
        return self.location_name

    def get_country(self):
        return self.country_name

