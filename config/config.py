from enum import Enum
from environs import Env

# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()

bot_token = env.str("bot_token")

bot_admins = [
    env.str("bot_admin_id"),
]

ip = env.str("ip")

proxy_url= env.str("proxy_url")
proxies_empty = {
      "http": None,
      "https": None,
    }

diag_flow_key_json = env.str("diag_flow_key_json")
diag_flow_project_id = env.str("diag_flow_project_id")

db_smart={}
db_smart["host"]=env.str("db_smart_host")
db_smart["port"]=env.int("db_smart_port")
db_smart["name"]=env.str("db_smart_name")
db_smart["user"]=env.str("db_smart_user")
db_smart["pwd"]=env.str("db_smart_pwd")

db_pgdev={}
db_pgdev["dbname"]=env.str("db_pgdev_dbname")
db_pgdev["host"]=env.str("db_pgdev_host")
db_pgdev["user"]=env.str("db_pgdev_user")
db_pgdev["pwd"]=env.str("db_pgdev_pwd")

mstr_server={}
mstr_server["user"]=env.str("mstr_server_user")
mstr_server["pwd"]=env.str("mstr_server_pwd")

ssrs_server={}
ssrs_server["adr"]=env.str("ssrs_adr")
ssrs_server["user"]=env.str("ssrs_user")
ssrs_server["pwd"]=env.str("ssrs_pwd")

mstr_api_11={}
mstr_api_11["user"] =env.str("mstr_api_11_user")
mstr_api_11["pwd"] =env.str("mstr_api_11_pwd")
mstr_api_11["url"] =env.str("mstr_api_11_url")

mstr_api_2020={}
mstr_api_2020["user"] =env.str("mstr_api_2020_user")
mstr_api_2020["pwd"] =env.str("mstr_api_2020_pwd")

mstr_library={}
mstr_library["user"] =env.str("mstr_library_user")
mstr_library["pwd"] =env.str("mstr_library_pwd")
mstr_library["url"] =env.str("mstr_library_url")

open_weather_api_key=env.str("open_weather_api_key")

class Projects(str, Enum):
    smart = '54A6A98611E854FF38BF0080EF657995'

class Documents(str, Enum):
    monthly_sales = dict(project=Projects.smart, document_id='7E51F60746ABB900C5F80BAFD9DE09E8')

config_monthly_sales = dict(
    months=dict(
            answer=dict(
                operator="equals",
                attribute={"id": "46165F2D4CD2A5C69AF19C8206556B3F", "name": "Месяц (сдвиг)"},
                form={"id": "45C11FA478E745FEA08D781CEA190FE5", "name": "ID"},
                ),
            prompt=dict(
                id="124C8BD94243FD36230412BB19F3B043",
                name="Qualification on Месяц(сдвиг)",
                type="EXPRESSION"
            )
    ),
    is_comparable=dict(
            answer=dict(
                operator="in",
                attribute={"id": "518D679440E8253243F2F19C509FD9AC", "name": "Признак Comparability магазина"},
                ),
            prompt=dict(
                id="F857ACCA4383976A634702A2B7CBAEC7",
                name="Qualification on Признак Comparable",
                type="EXPRESSION"
            )

    ),
    formats=dict(
            answer=dict(
                operator="in",
                attribute={"id": "3804C04645540FE1DBA3E185AD84C241"},
                ),
            prompt=dict(
                id="13D51AF34FF0CB57160009B966E2A015",
                name="Qualification on Формат",
                type="EXPRESSION"
            )

    ),
    do=dict(
            answer=dict(
                operator="in",
                attribute={"id": "2680B8504E76F6A8017A52BCCFF7F5CC"},
                ),
            prompt=dict(
                id="CA30BEFB40F6CBE2D183518C753FEF42",
                name="Qualification on Операционная дирекция",
                type="EXPRESSION"
            )

    ),
    stores=dict(
            answer=dict(),
            prompt=dict(
                id="0075B1B0415503128B3987A684552F92",
                name="Qualification on Магазин",
                type="EXPRESSION"
            )

    ),
)
