import os, math, requests, streamlit as st
st.set_page_config(page_title='NFL Odds Lab',page_icon='🏈',layout='centered')
st.title('🏈 NFL Odds Lab')
st.caption('FanDuel-focused • manual scan • no automatic wagering')

def decimal(american):
    a=int(american)
    if a==0 or -100<a<100: raise ValueError('Enter valid American odds, e.g. -110 or +150')
    return 1+a/100 if a>0 else 1+100/abs(a)

def american(d):
    return round((d-1)*100) if d>=2 else round(-100/(d-1))

def key():
    try: return st.secrets.get('ODDS_API_KEY','') or os.getenv('ODDS_API_KEY','')
    except Exception: return os.getenv('ODDS_API_KEY','')

@st.cache_data(ttl=120,show_spinner=False)
def odds(api_key):
    url='https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/'
    r=requests.get(url,params={'apiKey':api_key,'regions':'us','markets':'h2h,spreads,totals','oddsFormat':'american'},timeout=20)
    r.raise_for_status()
    return r.json()

if 'legs' not in st.session_state: st.session_state.legs=[]
t1,t2,t3=st.tabs(['🔎 Scan NFL','🧩 Parlay','💵 Payout'])
with t1:
    st.subheader('FanDuel NFL lines')
    api=key()
    if not api:
        st.info('Add ODDS_API_KEY in Streamlit app Secrets to enable live odds. The parlay and payout tools work now.')
    if st.button('Refresh NFL odds',disabled=not bool(api)):
        odds.clear()
    if api:
        try:
            games=odds(api)
            shown=0
            for game in games:
                book=next((b for b in game.get('bookmakers',[]) if b.get('key')=='fanduel'),None)
                if not book: continue
                shown+=1
                with st.expander(f"{game['away_team']} @ {game['home_team']} · {game['commence_time'][:16]} UTC"):
                    for market in book.get('markets',[]):
                        st.markdown('**'+{'h2h':'Moneyline','spreads':'Spread','totals':'Total'}.get(market['key'],market['key'])+'**')
                        for outcome in market.get('outcomes',[]):
                            name=outcome['name']+(f" {outcome['point']:+g}" if 'point' in outcome else '')
                            price=outcome['price']
                            st.write(f'{name}: {price:+d}')
                            if st.button('Add to parlay',key=f"{game['id']}-{market['key']}-{name}-{price}"):
                                st.session_state.legs.append({'pick':f"{game['away_team']} @ {game['home_team']} — {name}",'odds':price,'event':game['id']})
                                st.success('Added. Open Parlay tab.')
            if not shown: st.warning('No upcoming NFL games with FanDuel prices in the provider response.')
            st.caption('Prices may be delayed. Verify all selections in FanDuel before wagering. API usage may incur charges.')
        except requests.HTTPError as e: st.error(f'Odds provider error: {e}. Check API plan, key, and remaining quota.')
        except Exception as e: st.error(f'Could not load odds: {e}')
    st.caption('Player props require a separate supported event/props integration and suitable API coverage; not included in this version.')
with t2:
    st.subheader('Build your parlay')
    with st.form('manual'):
        pick=st.text_input('Pick description',placeholder='Player over 65.5 rushing yards')
        entered=st.text_input('American odds',value='+120')
        event=st.text_input('Game identifier (optional; useful for same-game warnings)')
        add=st.form_submit_button('Add selection')
        if add:
            try:
                d=decimal(int(entered.strip()))
                if not pick.strip(): st.error('Enter a selection name.')
                else:
                    st.session_state.legs.append({'pick':pick.strip(),'odds':int(entered),'event':event.strip()})
                    st.success('Selection added.')
            except ValueError as e: st.error(str(e))
    for i,leg in enumerate(st.session_state.legs):
        c1,c2=st.columns([5,1])
        c1.write(f"{i+1}. {leg['pick']} ({leg['odds']:+d})")
        if c2.button('✕',key=f'del{i}'):
            st.session_state.legs.pop(i); st.rerun()
    if st.button('Clear all legs'): st.session_state.legs=[]; st.rerun()
    if st.session_state.legs:
        d=math.prod(decimal(x['odds']) for x in st.session_state.legs)
        st.metric('Naive combined odds',f"{american(d):+d}")
        st.caption('Multiplication assumes independent legs. Same-game and correlated props may be repriced or rejected by FanDuel; this is NOT a sportsbook quote.')
with t3:
    st.subheader('Payout calculator')
    amount=st.number_input('Stake ($)',min_value=0.01,value=25.0,step=5.0)
    manual=st.text_input('Combined American odds (if not using saved legs)',value='+1000')
    boost=st.number_input('Profit boost (%)',min_value=0,max_value=500,value=0,step=10)
    use_legs=st.checkbox('Use parlay builder odds',value=bool(st.session_state.legs),disabled=not bool(st.session_state.legs))
    try:
        d=math.prod(decimal(x['odds']) for x in st.session_state.legs) if use_legs else decimal(int(manual.strip()))
        profit=amount*(d-1)*(1+boost/100)
        st.metric('Potential profit',f'${profit:,.2f}')
        st.metric('Total return',f'${amount+profit:,.2f}')
        st.caption(f'Unboosted implied probability: {100/d:.2f}%. This is not a model win probability. Boost assumes bonus applies to profit without a cap; check promotion terms.')
    except ValueError as e: st.error(str(e))
st.divider()
st.caption('For analysis only. No account access or bets placed. Bet only what you can afford to lose.')
