from bs4 import BeautifulSoup
import json

def get_leetcode_company_tags(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
        
    # Look for the __NEXT_DATA__ script tag which contains the companyTagStatsV2 data
    next_data_script = soup.find('script', id='__NEXT_DATA__')
    print(f"Found __NEXT_DATA__ script: {next_data_script is not None}")
    
    if next_data_script and next_data_script.string:
        try:
            # Parse the JSON data from the script tag
            next_data = json.loads(next_data_script.string)
            print("Successfully parsed __NEXT_DATA__ JSON")
            
            # Navigate through the exact path to find companyTagStatsV2
            # props.pageProps.dehydratedState.queries[1].state.data.question.companyTagStatsV2
            company_tag_stats = None
            
            try:
                # Follow the exact path provided by the user
                if len(next_data.get('props', {}).get('pageProps', {}).get('dehydratedState', {}).get('queries', [])) > 1:
                    # Access the second query (index 1)
                    query = next_data['props']['pageProps']['dehydratedState']['queries'][1]
                    if 'state' in query and 'data' in query['state'] and 'question' in query['state']['data']:
                        if 'companyTagStatsV2' in query['state']['data']['question']:
                            company_tag_stats = query['state']['data']['question']['companyTagStatsV2']
                            print(f"Found companyTagStatsV2 at the exact specified path")
            except (KeyError, IndexError) as e:
                print(f"Error following exact path: {str(e)}")
        except json.JSONDecodeError as e:
            print(f"Error parsing __NEXT_DATA__ JSON: {str(e)}")
        except Exception as e:
            print(f"Error extracting data from __NEXT_DATA__: {str(e)}")
            import traceback
            print(traceback.format_exc())
    return company_tag_stats
    