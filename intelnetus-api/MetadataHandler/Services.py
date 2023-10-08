from DbContext.Services import expand_column_size
from pybliometrics.scopus import AbstractRetrieval, AuthorRetrieval, AffiliationRetrieval
from Models.Collection import Publication, Author, Organization
from DataStore.Collection import get_scopus_fields, BLUE, RESET
from DataCleaner.Services import get_affiliations_ids
from WebSearch.Services import get_dois
from tqdm import tqdm
import re

def extract_metadata(keywords, year_published, fields, booleans, api_key, connection, cursor):

    scopus_fields = get_scopus_fields(fields)
    dois = get_dois(keywords, year_published, scopus_fields, booleans, api_key)

    for doi in tqdm(dois):
        try:
            publication_data = AbstractRetrieval(doi, view="FULL")
            publication_record = Publication(publication_data, year_published, doi)

            while True:
                try:
                    query = f"INSERT INTO scopus_publications VALUES('{publication_record.id}', \
                        '{publication_record.doi}','{publication_record.year}','{publication_record.title}',\
                        '{publication_record.journal}','{publication_record.abstract}','{publication_record.keywords}',\
                        '{publication_record.fields}','{publication_record.fields_abbreviations}',{publication_record.citations_count},\
                        {publication_record.authors_number},{publication_record.affiliations_number});"
                    
                    cursor.execute(query)
                    connection.commit()

                    currrent_publication_id = publication_record.id
                    publication_error_code = 0
                    break

                except Exception as publication_inserting_error:
                    publication_error_code = 1
                    if "Duplicate entry" not in str(publication_inserting_error):

                        if "Data too long" in str(publication_inserting_error):
                            pattern = r'\'+(.*?)\''
                            column_name = re.search(pattern, str(publication_inserting_error), re.IGNORECASE).group(1)

                            publication_attributes_sizes = {
                                "DOI": len(publication_record.doi),
                                "Title": len(publication_record.title),
                                "Abstract": len(publication_record.abstract),
                                "Keywords": len(publication_record.keywords),
                                "Journal": len(publication_record.journal),
                                "Fields": len(publication_record.fields),
                                "Fields_Abbreviations": len(publication_record.fields_abbreviations)
                            }

                            expand_column_size(publication_attributes_sizes[column_name], 'scopus_publications', column_name, connection, cursor)
                            
                        else:
                            publication_error_code = 2
                            print(f"{BLUE}Publication Metadatata Inserting Error Info:{RESET}\n"
                                f"DOI: {doi}\n"
                                f"Error: {str(publication_inserting_error)}")
                            break
                    else:
                        break

            if (publication_error_code == 0):                
                try:
                    authors = AbstractRetrieval(doi).authors

                    for author in authors:
                        author_data = AuthorRetrieval(author[0])
                        author_record = Author(author_data)

                        while True:
                            try:
                                query = f"INSERT INTO scopus_authors VALUES('{author_record.id}',\
                                    '{author_record.scopus_id}','{author_record.orcid_id}','{author_record.first_name}',\
                                    '{author_record.last_name}','{author_record.fields_of_study}','{author_record.affiliations}',\
                                     {author_record.h_index},{author_record.citations_count});"
                                
                                cursor.execute(query)
                                connection.commit()

                                current_author_id = author_record.id
                                author_error_code = 0
                                break

                            except Exception as author_inserting_error:
                                author_error_code = 1
                                if "Duplicate entry" not in str(author_inserting_error):
                                    if "Data too long" in str(author_inserting_error):
                                        pattern = r'\'+(.*?)\''
                                        column_name = re.search(pattern, str(author_inserting_error), re.IGNORECASE).group(1)  

                                        author_attributes_sizes = {
                                            "First_Name": len(author_record.first_name),
                                            "Last_Name": len(author_record.last_name),
                                            "Fields_Of_Study": len(author_record.fields_of_study),
                                            "Affiliations": len(author_record.affiliations)
                                        }     

                                        expand_column_size(author_attributes_sizes[column_name], 'scopus_authors', column_name, connection, cursor)
                                    
                                    else:
                                        author_error_code = 2
                                        print(f"{BLUE}Author Inserting Error Info:{RESET}\n"
                                            f"DOI: {doi}\n"
                                            f"Error: {str(author_inserting_error)}")
                                        break

                                else:
                                    query = f"SELECT ID FROM scopus_authors WHERE Scopus_ID = \'{author_record.scopus_id}\';"
                                    cursor.execute(query)
                                    current_author_id = cursor.fetchall()[0][0]
                                    break

                        if (author_error_code in [0, 1]):
                            query = f"INSERT INTO scopus_publications_authors VALUES('{currrent_publication_id}',\
                                     '{current_author_id}');"
                            cursor.execute(query)
                            connection.commit()

                            try:
                                authors = AbstractRetrieval(doi).authors

                                for author in authors:
                                    author_id = str(AuthorRetrieval(author[0]).identifier)
                                    affiliations = get_affiliations_ids(author[4])

                                    if ((affiliations != "-") & (author_id == author_record.scopus_id)):
                                        for affil in affiliations:
                                            affiliation_data = AffiliationRetrieval(int(affil), view="STANDARD")
                                            affiliation_record = Organization(affiliation_data)
                                            
                                            while True:
                                                try:
                                                    query = f"INSERT INTO scopus_organizations VALUES('{affiliation_record.id}',\
                                                            '{affiliation_record.scopus_id}','{affiliation_record.name}','{affiliation_record.type_1}',\
                                                            '{affiliation_record.type_2}','{affiliation_record.address}','{affiliation_record.city}',\
                                                            '{affiliation_record.country}');"
                                                    
                                                    cursor.execute(query)
                                                    connection.commit()

                                                    current_affiliation_id = affiliation_record.id
                                                    affliliation_error_code = 0
                                                    break

                                                except Exception as affiliation_inserting_error:
                                                    affliliation_error_code = 1

                                                    if "Duplicate entry" not in str(affiliation_inserting_error):
                                                        if "Data too long" in str(affiliation_inserting_error):
                                                            pattern = r'\'+(.*?)\''
                                                            column_name = re.search(pattern, str(affiliation_inserting_error), re.IGNORECASE).group(1)
                                                            
                                                            affiliation_attributes_sizes = {
                                                                "Name": len(affiliation_record.name),
                                                                "Address": len(affiliation_record.address),
                                                                "City": len(affiliation_record.city),
                                                                "Country": len(affiliation_record.country)
                                                            }

                                                            expand_column_size(affiliation_attributes_sizes[column_name], "scopus_organizations", column_name, connection, cursor)
                                                        
                                                        else:
                                                            affliliation_error_code = 2
                                                            print(f"{BLUE}Organization Inserting Error Info:{RESET}\n"
                                                                f"DOI: {doi}\n"
                                                                f"Affiliation Scopus ID: {affiliation_record.scopus_id}\n"
                                                                f"Error: {str(affiliation_inserting_error)}")
                                                            break

                                                    else:
                                                        query = f"SELECT ID FROM scopus_organizations WHERE Scopus_ID = \'{affiliation_record.scopus_id}\';"
                                                        cursor.execute(query)
                                                        current_affiliation_id = cursor.fetchall()[0][0]
                                                        break

                                            if (affliliation_error_code in [0, 1]):
                                                try:
                                                    query = f"INSERT INTO scopus_publications_organizations VALUES('{currrent_publication_id}', \
                                                        '{current_affiliation_id}');"
                                                    cursor.execute(query)
                                                    connection.commit()

                                                except Exception as publication_affiliation_inserting_error:
                                                    if "Duplicate entry" not in str(publication_affiliation_inserting_error):
                                                        print(f"{BLUE}Publications - Organizations Inserting Error Info:{RESET}\n"
                                                            f"DOI: {doi}\n"
                                                            f"Affiliation Scopus ID: {affiliation_record.scopus_id}\n"
                                                            f"Error: {str(publication_affiliation_inserting_error)}")

                                                try:
                                                    query = f"INSERT INTO scopus_authors_organizations VALUES('{current_author_id}', \
                                                        '{current_affiliation_id}',{year_published});"
                                                    cursor.execute(query)
                                                    connection.commit()

                                                except Exception as author_affiliation_inserting_error:
                                                    if "Duplicate entry" not in str(author_affiliation_inserting_error):
                                                        print(f"{BLUE}Authors - Organizations Inserting Error Info:{RESET}\n"
                                                            f"DOI: {doi}\n"
                                                            f"Affiliation Scopus ID: {affiliation_record.scopus_id}\n"
                                                            f"Error: {str(author_affiliation_inserting_error)}")

                            except Exception as affiliation_ogranization_error:
                                print(f"{BLUE}Organization Retrieving Error Info:{RESET}\n"
                                    f"DOI: {doi}\n"
                                    f"Affiliation Scopus ID: {affiliation_record.scopus_id}\n"
                                    f"Error: {str(affiliation_ogranization_error)}")
                                pass

                except Exception as author_retrieving_error:
                    print(f"{BLUE}Author Retrieving Error Info:{RESET}\n"
                        f"DOI: {doi}\n"
                        f"Error: {str(author_retrieving_error)}")
                    pass

        except Exception as publication_retrieving_error:
            print(f"{BLUE}Publication Retrieving Error Info:{RESET}\n"
                f"DOI: {doi}\n"
                f"Error: {str(publication_retrieving_error)}")
            pass