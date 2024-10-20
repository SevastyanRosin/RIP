import random

from django.core.management.base import BaseCommand
from minio import Minio

from ...models import *
from .utils import random_date, random_timedelta, random_bool


def add_users():
    User.objects.create_user("user", "user@user.com", "1234", first_name="user", last_name="user")
    User.objects.create_superuser("root", "root@root.com", "1234", first_name="root", last_name="root")

    for i in range(1, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234", first_name=f"user{i}", last_name=f"user{i}")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234", first_name=f"user{i}", last_name=f"user{i}")

    print("Пользователи созданы")


def add_units():
    Unit.objects.create(
        name="Отдел безопасности и охраны",
        description="• Обеспечение надежной защиты объектов филиала от краж, хищений, грабежей, других преступных посягательств и общественных беспорядков;\n• Обеспечение инженерно-технической защиты Филиала;\n• Обеспечение на охраняемых объектах контрольно-пропускного и внутриобъектового режима, предупреждение и пресечение хищений материальных ценностей;\n• Пресечение попыток несанкционированного проникновения на объекты филиала посторонних лиц;\n• Установление порядка допуска сотрудников сторонних организаций, посетителей и транспортных средств на охраняемую территорию;",
        phone="8 904 815 31 92",
        image="1.png"
    )

    Unit.objects.create(
        name="Ученый совет",
        description="• Рассмотрение вопросов текущей деятельности и развития Филиала в целях обеспечения высокого качества подготовки выпускников;\n• Методическое руководство и координация деятельности Филиала в сфере: учебной работы, научно-исследовательской работы, кадровой и административной работы, социальной работы.",
        phone="8 914 825 51 52",
        image="2.png"
    )

    Unit.objects.create(
        name="Отдел инженерной эксплуатации",
        description="• Поддержка учебных корпусов, зданий общежитий в состоянии, обеспечивающем их долголетнюю и надежную работу. Для этого подразделение проводит техническую эксплуатацию зданий, профилактику их конструкций, осуществляет проведение текущего ремонта зданий, поддерживать инженерные системы в учебных корпусах и зданиях общежитий в состоянии, обеспечивающем их долголетнюю и надежную работу.\n• Поддержка электротехнических систем в учебных корпусах и зданиях общежитий в состоянии, обеспечивающем их долголетнюю и надежную работу. Для этого подразделение проводит их техническую эксплуатацию и профилактику конструкций, узлов оборудования и приборов.",
        phone="8 753 215 35 11",
        image="3.png"
    )

    Unit.objects.create(
        name="Отдел научной и инновационной деятельности",
        description="• Координация, организационно-методическая поддержка и контроль выполнения по веществам отраслей НИОКР с целью создания образцов машин, оборудования, материалов, новых технологических процессов, решения важных социальных и экологических задач, совершенствования организации труда и управления.\n• Организация проведения фундаментальных исследований по Программам федерального и регионального правительств, направленных на инновационное развитие Калужского региона.\n• Организация научных, технологических, организационных, финансовых и коммерческих мероприятий, направленных на коммерциализацию накопленных знаний, технологий и оборудования.\n• Содействие повышению качества подготовки специалистов и научно-педагогических кадров, росту квалификации профессорско-преподавательского состава филиала.\n• Организация учета, анализа и оформления результатов научно-технической деятельности Филиала, создание базы данных научно-технических достижений.",
        phone="8 324 315 41 32",
        image="4.png"
    )

    Unit.objects.create(
        name="Бухгалтерия",
        description="• Исполнение «Учётной политики Университета в соответствии с законодательством о бухгалтерском и налоговом учёте, обеспечивая финансовую устойчивость филиала;\n• Учёт имущества, обязательств и хозяйственных операций, поступающих основных средств, товарно-материальных ценностей, денежных средств;\n• Начисление и выплата в установленные сроки зарплаты, стипендий, пособий и других выплат;\n• Своевременное проведение расчетов с юридическими и физическими лицами; уплата всех видов налогов и сборов;\n• Ведение учёта федеральных средств, целевых поступлений, доходов и расходов по средствам, полученных от иных источников;\n•",
        phone="8 544 835 47 48",
        image="5.png"
    )

    Unit.objects.create(
        name="Юридический отдел",
        description="• осуществление единого исполнения функциональных обязанностей юридической службы в деятельности структурных подразделений Филиала под непосредственным его руководством;\n• обеспечение правовой безопасности образовательной, научной, международной, финансово-хозяйственной и других видов уставной деятельности, осуществляемых Филиалом;\n• методологическое обеспечение правовой работы в деятельности Филиала;\n• организация эффективного использования и учета недвижимого имущества, в том числе путем сдачи его в аренду;",
        phone="8 334 515 32 80",
        image="6.png"
    )

    client = Minio("minio:9000", "minio", "minio123", secure=False)
    client.fput_object('images', '1.png', "app/static/images/1.png")
    client.fput_object('images', '2.png', "app/static/images/2.png")
    client.fput_object('images', '3.png', "app/static/images/3.png")
    client.fput_object('images', '4.png', "app/static/images/4.png")
    client.fput_object('images', '5.png', "app/static/images/5.png")
    client.fput_object('images', '6.png', "app/static/images/6.png")
    client.fput_object('images', 'default.png', "app/static/images/default.png")

    print("Услуги добавлены")


def add_orders():
    users = User.objects.filter(is_staff=False)
    moderators = User.objects.filter(is_staff=True)

    if len(users) == 0 or len(moderators) == 0:
        print("Заявки не могут быть добавлены. Сначала добавьте пользователей с помощью команды add_users")
        return

    units = Unit.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        owner = random.choice(users)
        add_order(status, units, owner, moderators)

    add_order(1, units, users[0], moderators)
    add_order(2, units, users[0], moderators)

    print("Заявки добавлены")


def add_order(status, units, owner, moderators):
    order = Order.objects.create()
    order.status = status

    if order.status in [3, 4]:
        order.date_complete = random_date()
        order.date_formation = order.date_complete - random_timedelta()
        order.date_created = order.date_formation - random_timedelta()
    else:
        order.date_formation = random_date()
        order.date_created = order.date_formation - random_timedelta()

    order.owner = owner
    order.moderator = random.choice(moderators)

    order.name = "Название приказа"
    order.description = "Описание приказа"
    order.date = random_date()

    for unit in random.sample(list(units), 3):
        item = UnitOrder(
            order=order,
            unit=unit,
            value=random_bool()
        )
        item.save()

    order.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_units()
        add_orders()
