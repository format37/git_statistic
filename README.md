# git_statistic
Generating a report on GitHub python libraries usage
### Installation
```
git clone https://github.com/format37/git_statistic.git
cd git_statistic
pip install -r requirements.txt
```
### Usage
* Obtain your github api key
Run:
```
python3 download.py
```
* Fill the cat.json file with corresponding categories.  
For example:
```
{
    "cv2": "CV",
    "numpy": "ML",
    "pandas": "ML"
}
```
Run:
```
python3 report.py
```
Now you can publish your report.html file. In your github repo for example.
