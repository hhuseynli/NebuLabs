from demo_seed_common import ScenarioProfile, parse_args, seed_scenario


if __name__ == "__main__":
    args = parse_args(default_slug="cultify-uptrend-demo")
    seed_scenario(
        ScenarioProfile(
            name="Rising Momentum",
            post_count=16,
            comments_per_post=10,
            votes_per_post=24,
            mood="uptrend",
        ),
        api_base=args.api_base,
        slug=args.slug,
        seed=args.seed,
    )
