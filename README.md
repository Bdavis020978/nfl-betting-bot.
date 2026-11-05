# NFL Odds Lab — iPhone Safari app

A mobile-friendly Streamlit app with a manual FanDuel NFL odds scanner (moneyline/spread/total), parlay builder, and payout calculator. It does **not** place bets, provide a predictive AI model, fetch player props, or run background alerts. Parlay math assumes independent legs and is not a FanDuel same-game-parlay quote.

## Deploy without a computer
1. On iPhone Safari, create a GitHub account at https://github.com if needed.
2. Create a **private** GitHub repository named `nfl-odds-lab`.
3. Use GitHub's **Add file → Upload files** to upload `app.py` and `requirements.txt` from this zip (README optional). Commit changes.
4. Visit https://share.streamlit.io and sign in with GitHub. Authorize private repo access if prompted.
5. Select **Create app → Yup, I have an app**. Select your repository, `main` branch and `app.py` entrypoint. Deploy.
6. For live FanDuel odds, obtain an API key from https://the-odds-api.com/ . In the Streamlit deployment's **Advanced settings → Secrets** (or app settings after deployment), add:
   ```toml
   ODDS_API_KEY = "paste_your_key_here"
   ```
   Never put your key in GitHub files. Confirm your API plan includes NFL and US bookmakers. API calls consume quota.
7. Open your deployed `*.streamlit.app` URL in Safari, tap Share → Add to Home Screen.

## Notes
- The scanner refreshes when requested and caches results for 120 seconds. It does not monitor when closed.
- If the provider returns no FanDuel markets, the app displays a message rather than inventing odds.
- Manually added props can be used in parlay arithmetic but are not verified against FanDuel.
- Streamlit session state is temporary; your selections may disappear when the app restarts.
- For private access, check your Streamlit Community Cloud sharing and viewer permissions.
