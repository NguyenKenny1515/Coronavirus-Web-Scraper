# ----------------------------------------------------------------------
# Name:        coronavirus
# Purpose:     Compiles coronavirus information from multiple web pages
# and save that information in a text file on the user's computer
#
# Author(s): Kenny Nguyen
# ----------------------------------------------------------------------
import urllib.request
import urllib.error
import urllib.parse
import bs4
import re


def country_coronavirus_stats(search_term):
    """
    Extract needed information (cases, deaths, population, etc.) of
    given country(ies) and then write it to a summary file
    :param search_term: (string) given country(ies) to extract info
    :return: None
    """
    soup = read_url("https://en.wikipedia.org/wiki/2019%E2%80"
                    "%9320_coronavirus_pandemic_by_country_and_territory")
    table = soup.find('table', id='thetable')
    regex = re.compile(search_term, re.IGNORECASE)
    countries_links = table.find_all('a', string=regex)
    countries = {}

    for country in countries_links:
        if not country.get("href", None).\
                startswith("/wiki/2020_coronavirus_pandemic_in_"):
            continue

        cases = int(country.find_next('td').get_text().replace(",", ""))
        deaths = int(country.find_next('td').find_next('td').get_text().
                     replace(",", ""))
        link = urllib.parse.urljoin("https://en.wikipedia.org",
                                    country.get("href", None))
        first_paragraph = get_first_paragraph(link)
        population = get_population(country.get_text())
        cases_per_100000 = calculate_per_100000_stat(population, cases)
        deaths_per_100000 = calculate_per_100000_stat(population, deaths)

        countries[country.get_text()] = (f'{population:,}', f'{cases:,}',
                                         f'{deaths:,}', cases_per_100000,
                                         deaths_per_100000, first_paragraph)

    create_summary_file(search_term, countries)


def read_url(url):
    """
    Open the given url and return corresponding BeautifulSoup object
    :param url: (string) address of the web page to be read
    :return: BeautifulSoup object
    """
    try:
        with urllib.request.urlopen(url) as url_file:
            url_bytes = url_file.read()
    except urllib.error.URLError as url_err:
        print(f'Error opening url: {url}\n{url_err}')
    else:
        soup = bs4.BeautifulSoup(url_bytes, 'html.parser')
        return soup


def get_first_paragraph(url):
    """
    Extract the first non-empty visible paragraph from given url
    :param url: (string) country link from url table
    :return: (string) first non-empty visible paragraph on the page
    """
    soup = read_url(url)
    pattern = r'..*\n'
    for p_tag in soup("p"):
        if re.match(pattern, p_tag.get_text()):
            return p_tag.get_text()


def get_population(country):
    """
    Extract the total population for given country
    :param country: (string) country to search for in url
    :return: (integer) population of the country
    """
    soup = read_url("https://en.wikipedia.org/wiki/List_of_countries_and_"
                    "dependencies_by_population")
    table = soup('table')[0]
    regex = re.compile(country, re.IGNORECASE)
    country_row = table.find_all('a', string=regex)
    return int(country_row[0].find_next("td").get_text().replace(",", ""))


def calculate_per_100000_stat(population, stat):
    """
    Convert given stat to per 100000 stat based on population
    :param population: (int) the population of a country
    :param stat: (int) a statistic of a country
    :return: (float) per 100000 version of the stat
    """
    if stat == 0:
        return 0.0
    converted_population = population / 100000
    return round(stat / converted_population, 1)


def create_summary_file(search_term, countries):
    """
    Write info collected for all countries that match the search term in
    new file
    :param search_term: (string) term that file will be named after
    :param countries: (dictionary) the countries as keys and their info
    as values
    :return: None
    """
    with open(f'{search_term}summary.txt', 'x', encoding='utf-8') as \
            summary_file:
        for country in countries:
            population, cases, deaths, cases_per_100000, deaths_per_100000, \
                first_paragraph = countries[country]
            summary_file.write(f'Country: {country}\n'
                               f'Population:{population:>30}\n'
                               f'Total Confirmed Cases:{cases:>19}\n'
                               f'Total Deaths:{deaths:>28}\n'
                               f'Cases per 100,000 people:'
                               f'{cases_per_100000:>18}\n'
                               f'Deaths per 100,000 people:'
                               f'{deaths_per_100000:>17}\n'
                               f'{first_paragraph}\n\n')


def main():
    search_term = input("Please enter a search term: ")
    country_coronavirus_stats(search_term)
    print(f'Your data has been saved in the file: '
          f'{search_term.lower()}summary.txt.')


if __name__ == '__main__':
    main()
