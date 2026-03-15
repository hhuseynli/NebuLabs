from demo_seed_common import ScenarioProfile, parse_args, seed_scenario


if __name__ == "__main__":
    args = parse_args(default_slug="cultify-decline-demo")
    seed_scenario(
        ScenarioProfile(
            name="Attention Decline",
            post_count=4,
            comments_per_post=1,
            votes_per_post=3,
            mood="decline",
        ),
        api_base=args.api_base,
        slug=args.slug,
        seed=args.seed,
    )
