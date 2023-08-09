# JAKT
Jakt is just another (k)ommand-line timetracker tool. 

⚠️ Jakt is under heavy development: Breaking changes can occur at any moment. ⚠️  
If you find an issue please submit it [here](https://github.com/kwillno/jakt/issues).

## But what is it? 
Jakt helps you keep track of how you spend your time. Whether you want to keep better track of how much time you spend on each project or want to keep yourself accountable while working, jakt is the perfect tool.

## The name
The name comes from the norwegian word for hunt. Timetracking is one of the best tools in your arsenal in your hunt for productivity.  
And if you are wondering, yes, I started with the acronym. 

## Features
Jakt is a tool for timetracking. It has support for:
- [x] Projects
- [x] Tags
- [x] Live tracking from commandline
- [ ] Manually adding time that is not tracked live
- [x] A python library that can be used in other applications

For feature requests please open an [issue](https://github.com/kwillno/jakt/issues).

## Installation
Jakt can be installed from PyPI using:
```
pip install jakt
```

You can then start using jakt by simply typing 
```
jakt start <PROJECT> <[TAGS]>
```
in any terminal.

### From Source
1. Clone the repo
2. `cd jakt` 
3. `pip install -e .`  
	Make sure to use the correct version of pip, some users will need to use `pip3` instead. 

If you intend to develop with Jakt as well as using it for timetracking there is a step 4:  

4. `jakt debug true`  

This way you can create a testing environment without risking your tracked timeslots. The only file that is accessed by both environments is the configfile. 


## License 
This project is licensed under the MIT License. See [LICENSE](https://github.com/kwillno/jakt/blob/main/LICENSE). 
