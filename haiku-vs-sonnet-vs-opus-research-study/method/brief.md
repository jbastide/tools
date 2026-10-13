You are gathering sources for a writer. Do the research only. Do not write an article.

TOPIC
Does Google record the phone calls people make to law firms from Google's ads (Local Services Ads, and Google Ads call ads, call assets and website call tracking), and what follows from that for a law firm in the United States?

QUESTIONS
Q1. Does Google record calls that come from Local Services Ads? Which calls, in which countries?
Q2. Does Google record calls from Google Ads (call ads, call assets, calls from a website)? Is recording on by default, and under what conditions does it apply?
Q3. What does the caller hear before a recorded call, and what does the business hear?
Q4. How long does Google keep the recordings, or keep them playable? Is there a different period for legal categories?
Q5. Who can listen to the recordings, and what does Google say it uses them for (including any AI analysis)?
Q6. Can a business turn the recording off? Where, and what changes when it does?
Q7. Which business categories does Google exclude from call recording? Are legal services among them?
Q8. What have US state bars, bar ethics counsel or ethics committees published about recorded calls from Google's ads (confidentiality, privilege, prospective clients)? Give the state, the document, its date and its current status.
Q9. What do lawyers, law firm staff or their marketers say first-hand in public threads (Reddit, Google Ads Community, lawyer forums, similar) about Google recording these calls? Find up to 8 threads.
Q10. What do Google's terms require the advertiser to have told, or obtained from, its own staff and callers about recording?

RULES
1. Use web search and web fetch (you may need to load them through tool search). You may use shell commands such as curl to read a web page. Save every file you create inside your own folder, given below, and nowhere else. Other researchers are working on the same brief in other folders at the same time: do not read, list or search any folder but yours, and do not read any other file on this machine.
2. Do not open or cite copyfororiginals.com or any of its subdomains.
3. Prefer primary sources: Google's own help pages and terms, and the bar's own publication. Use a secondary source only when the primary one cannot be reached, and say so in the claim's "note".
4. One fact per claim, stated in one sentence in your own words.
5. Every claim needs the URL of the page where you read it and a quote copied character for character from that page: one continuous passage, at most 300 characters, no ellipses, no stitching passages together, no corrections. Every quote will be machine-checked against the page at that URL. If you cannot get the exact words, do not make it a claim. Put it under "leads" instead.
6. If you looked for something and could not find it, list it under "not_found". Do not guess and do not fill gaps from memory.
7. Stay within about 60 tool calls.
8. Write your output as one valid JSON file named output.json in your folder. Then reply with one short paragraph: how many claims, how many distinct URLs, and which questions you could not answer.

OUTPUT SCHEMA
{
  "claims": [
    {
      "id": "c1",
      "question": "Q1",
      "claim": "one sentence in your own words",
      "url": "https://...",
      "quote": "verbatim passage from that page",
      "source_type": "google_help | google_terms | state_bar | court_or_regulator | thread | news_or_blog | other",
      "source_date": "date on the page if it shows one, else empty",
      "note": "optional"
    }
  ],
  "leads": [
    {"question": "Q9", "what": "what you think is there", "url": "https://...", "why_not_a_claim": "could not open the page"}
  ],
  "not_found": [
    {"question": "Q4", "what": "what you looked for and did not find"}
  ]
}

YOUR FOLDER
{FOLDER}
