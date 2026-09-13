from datetime import timedelta

PERMIT_DURATION = timedelta(hours=7, minutes=59)   # hvor længe én tilladelse rent faktisk er gyldig
RENEWAL_INTERVAL = timedelta(hours=7, minutes=45)   # hvornår vi fornyer (15 min margin)


def compute_schedule(start, end):
    if end is None:
        return [start]

    schedule = [start]
    covered_until = start + PERMIT_DURATION

    while covered_until < end:
        next_reg = schedule[-1] + RENEWAL_INTERVAL
        schedule.append(next_reg)
        covered_until = next_reg + PERMIT_DURATION

    return schedule


if __name__ == "__main__":
    from datetime import datetime

    single = compute_schedule(datetime(2026, 9, 7, 13, 0), None)
    print("Enkelt registrering:", single)

    range1 = compute_schedule(datetime(2026, 9, 8, 10, 0), datetime(2026, 9, 8, 20, 0))
    print("10-20 i morgen:", range1)

    range2 = compute_schedule(datetime(2026, 9, 15, 14, 0), datetime(2026, 9, 18, 10, 0))
    print("Flerdages-ophold:", range2)
