from backend.database import SessionLocal, Base, engine
from backend.aggregator import aggregate_usage
import argparse


def main():
    parser = argparse.ArgumentParser(description='Aggregate reservations into timeseries (daily/weekly).')
    parser.add_argument('--days', type=int, default=60, help='Lookback days for daily aggregation (default: 60)')
    parser.add_argument('--weeks', type=int, default=12, help='Lookback weeks for weekly aggregation (default: 12)')
    parser.add_argument('--series-daily', default='seat_usage_daily', help='Series name for daily aggregation')
    parser.add_argument('--series-weekly', default='seat_usage_weekly', help='Series name for weekly aggregation')
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        d, w = aggregate_usage(db, lookback_days=args.days, lookback_weeks=args.weeks, series_daily=args.series_daily, series_weekly=args.series_weekly)
        print(f"Aggregated: daily_inserted={d}, weekly_inserted={w}")
    finally:
        db.close()


if __name__ == '__main__':
    main()

