from demo_seed_common import ScenarioProfile, parse_args, seed_scenario


if __name__ == "__main__":
    args = parse_args(default_slug="cultify-regular-demo")
    seed_scenario(
        ScenarioProfile(
            name="Regular Sentiment",
            post_count=8,
            comments_per_post=5,
            votes_per_post=10,
            mood="regular",
        ),
        api_base=args.api_base,
        slug=args.slug,
        seed=args.seed,
    )
