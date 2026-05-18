from prometheus_client import Counter

BOOKINGS_CREATED = Counter(
    "bookings_created_total",
    "Total number of bookings created",
    ["hotel_id"],
)

BOOKINGS_CANCELLED = Counter(
    "bookings_cancelled_total",
    "Total number of cancelled bookings",
)

USERS_REGISTERED = Counter(
    "users_registered_total",
    "Total number of registered users",
)
