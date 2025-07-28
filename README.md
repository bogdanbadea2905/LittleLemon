## API & View Endpoints

| Path                                        | View/Descriere                          |
| ------------------------------------------- | --------------------------------------- |
| `/`                                         | Home page                               |
| `/about/`                                   | About page                              |
| `/book/`                                    | Book a table (form)                     |
| `/reservations/`                            | List reservations (HTML)                |
| `/bookings/`                                | Bookings API (JSON)                     |
| `/menu/`                                    | Menu page (HTML)                        |
| `/menu/<int:pk>/`                           | Single menu item (HTML)                 |
| `/menu-items/`                              | Menu items API (GET, POST)              |
| `/menu-items/<int:pk>/`                     | Single menu item API (GET, PUT, DELETE) |
| `/menu-items/featured/`                     | Item of the day (GET, POST)             |
| `/categories/`                              | Categories API                          |
| `/token-auth/`                              | Obtain auth token (login)               |
| `/groups/manager/users/`                    | Manager group users (GET, POST)         |
| `/groups/manager/users/<int:userId>/`       | Remove manager user (DELETE)            |
| `/groups/delivery-crew/users/`              | Delivery crew group users (GET, POST)   |
| `/groups/delivery-crew/users/<int:userId>/` | Remove delivery crew user (DELETE)      |
| `/cart/menu-items/`                         | Cart API (GET, POST, DELETE)            |
| `/orders/`                                  | Orders API (GET, POST)                  |
| `/orders/<int:pk>/`                         | Order detail API (GET, PUT, DELETE)     |

> For authentication and registration, see also the `/auth/` routes provided by Djoser.
