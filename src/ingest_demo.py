from datetime import date, timedelta

from .legal_pipeline import InfraiClient, MatterIntake, deadline_follow_up, ingest_matter, signed_delivery


def main() -> None:
    intake = MatterIntake("matter-042", "Signed lease amendment received. Review notice period and renewal clause.", "counsel@example.org", date.today() + timedelta(days=7))
    client = InfraiClient()
    print(ingest_matter(client, intake))
    print(signed_delivery(intake))
    print({"follow_up": deadline_follow_up(intake.deadline)})


if __name__ == "__main__":
    main()

