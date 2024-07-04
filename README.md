# git_statistic
Generating a report on GitHub python libraries usage
### Installation
```
git clone https://github.com/format37/git_statistic.git
cd git_statistic
pip install -r requirements.txt
```
### Usage
* Obtain your github [api key](https://github.com/settings/tokens?type=beta)
Run:
```
python3 download.py
```
* Fill the categories list automatically using cat_retriever.ipynb script. You can define the cat_count if you need to decrease or increase the number of categories.
* Fill the enabled_categories.txt by categoruies that you need to enable by default in the report.  
* Run:
```
python3 report.py
python3 timeline.py
md_report.py
```
Now you can publish or share your html reports. For example [report.html](https://format37.github.io/git_statistic/report_rwa.html) file.