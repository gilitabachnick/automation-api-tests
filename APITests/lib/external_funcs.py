class external_funcs:
    
    def get_git_file_contents(self, token, repo, path):
        from github import Github
        try:
            login = Github(token)
            org = login.get_organization('kaltura')
            repository = org.get_repo(repo)
            git_file = repository.get_contents(path)
            result = git_file.decoded_content
        except Exception as exp:
            result = False
            print(exp)           
        return result
    
    def get_confluence_page(self, confluence_page_id, user, token):
        import requests
        from bs4 import BeautifulSoup
        try:
            params = (('expand', 'body.storage'),)
            page = 'https://kaltura.atlassian.net/wiki/rest/api/content/' + confluence_page_id
            response = requests.get(page, 
                            params=params, 
                            auth=(user, token))
            result = BeautifulSoup(response.text, 'html.parser')
        except Exception as exp:
            result = False
            print(exp)           
        return result