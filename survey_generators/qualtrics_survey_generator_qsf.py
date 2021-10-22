import pandas as pd 
import json
import math
import sys
import numpy as np
import copy

# The Mturk question: In order to get paid for the work you have done on this survey, you need to enter the following code in the box at the bottom of the Mechanical Turk page where you started once you close this survey.

# Please write this down so you don't forget:

# ${rand://int/10000:99999}

np.random.seed(0)

# survey settings
all_titles = list(pd.read_csv("../input_headlines/ra_data.csv", encoding = 'utf8')["Headline"])

num_headlines = 50 # unique titles to be classified
num_students = 5 # number of people taking this survey version
overlap = 0.2 # percent of headlines assigned to 1 respondent that will be duplicated
training_length = 5 # number of training titles
training_headlines = ["Training headline {}".format(i) for i in range(training_length)]
training_answers = [np.random.randint(4) for i in range(len(training_headlines))]
block_size = 3 # number of questions in a block (between attention-check)

training_thresh = 0.9
attention_thresh = 0.9

conditional = False

survey_name = "MTurk Trial"
assignments_name = "../respondent_assignments/mturk_assignments.json"
qsf_name = "../qsf_output/mturk_trial_refactored.qsf"

titles = np.array(all_titles)

# determine indices for headlines assigned to each student
titles_per_student = math.ceil(num_headlines / ((1 - overlap) * num_students))
uniques_per_student = math.floor(num_headlines / num_students)

attention_check_length = 2 # number of questions in an attention-check block
attention_check_headlines = [["Attention check headline {}, Block {}".format(i, j) for i in range(attention_check_length)] for j in range(math.ceil(titles_per_student / block_size))]
calc_attention_thresh = [math.ceil(len(i) * attention_thresh) for i in attention_check_headlines]

attention_check_answers = {}
for i in attention_check_headlines:
	for j in i:
		attention_check_answers[j] = [np.random.randint(4), "Acquirer", "Acquired"]

uniques_left = num_headlines - num_students * uniques_per_student
uniques = [uniques_per_student for i in range(num_students)]
idx = 0
while uniques_left:
	uniques[idx] += 1
	idx = (idx + 1) % num_students
	uniques_left -= 1

student_assignments = {}
idx_set = set(range(num_headlines))
for i in range(num_students):
	unique_selection = np.random.choice(list(idx_set), size = uniques[i], replace = False)
	idx_set = idx_set - set(unique_selection)
	student_assignments[i] = list(unique_selection)

dup_selection_lst = []
for i in range(num_students):
	dup_selection = np.random.choice(list(student_assignments[(i - 1) % num_students]), size = titles_per_student - uniques[i], replace = False)
	dup_selection_lst.append(list(dup_selection))

x = []
for i in range(num_students):
	student_assignments[i].extend(dup_selection_lst[i])

student_assignments_json = {}
titles_to_classify = []
for student, assignments in student_assignments.items():
	student_assignments_json[str(student)] = [titles[a] for a in assignments]
	titles_to_classify.append(student_assignments_json[str(student)])
titles_to_classify = list(set(np.array(titles_to_classify).flatten()))

with open(assignments_name, 'w') as f:
	json.dump(student_assignments_json, f, ensure_ascii = False, indent = 2)

survey_info = {}

# args needed: flow id, right operand, right operand
branch_logic_template = {
	"Type": "Branch",
	"FlowID": "",
	"Description": "New Branch",
	"BranchLogic": {
		"0": {
			"0": {
				"LogicType": "EmbeddedField",
				"LeftOperand": "Score",
				"Operator": "LessThan",
				"RightOperand": "",
				"_HiddenExpression": False,
				"Type": "Expression",
				"Description": "<span class=\"ConjDesc\">If</span>  <span class=\"LeftOpDesc\">Score</span> <span class=\"OpDesc\">Is Less Than</span> <span class=\"RightOpDesc\"> "" </span>"
			},
			"Type": "If"
		},
		"Type": "BooleanExpression"
	}
}

end_survey_display = {
		"ID": "BL_{}",
		"Type": "Block",
		"FlowID": "FL_{}"
}
end_survey = {
	"Type": "EndSurvey",
	"FlowID": "FL_-500"
}

set_score = {
	"Type": "EmbeddedData",
	"FlowID": "FL_0",
	"EmbeddedData": [
		{
		"Description": "Score",
		"Type": "Custom",
		"Field": "Score",
		"VariableType": "String",
		"DataVisibility": [],
		"AnalyzeText": False,
		"Value": "${gr://SC_0/Score}"
		}
	]
}

survey_info["SurveyEntry"] = {
	"SurveyID": "SV_eLnpGNWb3hM31cy",
	"SurveyName": survey_name,
	"SurveyDescription": None,
	"SurveyOwnerID": "UR_3WUHDMGK0A1YPvo",
	"SurveyBrandID": "",
	"DivisionID": "DV_bCz0vLDEYcivdHv",
	"SurveyLanguage": "EN",
	"SurveyActiveResponseSet": "RS_dgMRsbI5TIbBjLw",
	"SurveyStatus": "Inactive",
	"SurveyStartDate": "0000-00-00 00:00:00",
	"SurveyExpirationDate": "0000-00-00 00:00:00",
	"SurveyCreationDate": "2021-09-02 21:33:29",
	"CreatorID": "UR_3WUHDMGK0A1YPvo",
	"LastModified": "2021-09-02 21:35:33",
	"LastAccessed": "0000-00-00 00:00:00",
	"LastActivated": "0000-00-00 00:00:00",
	"Deleted": None,
}

survey_info["SurveyElements"] = [
	{
		"SurveyID": "SV_eLnpGNWb3hM31cy",
		"Element": "BL",
		"PrimaryAttribute": "Survey Blocks",
		"SecondaryAttribute": None,
		"TertiaryAttribute": None,
		"Payload": [],
	},
	{
      "SurveyID": "SV_eLnpGNWb3hM31cy",
      "Element": "FL",
      "PrimaryAttribute": "Survey Flow",
      "SecondaryAttribute": None,
      "TertiaryAttribute": None,
      "Payload": {
      	"Type": "Root",
      	"FlowID": "FL_1",
        "Flow": [],
        "Properties": {
          "Count": 3,
        },
      }
    },
    {
      "SurveyID": "SV_eLnpGNWb3hM31cy",
      "Element": "SO",
      "PrimaryAttribute": "Survey Options",
      "SecondaryAttribute": None,
      "TertiaryAttribute": None,
      "Payload": {
        "BackButton": "false",
        "SaveAndContinue": "true",
        "SurveyProtection": "PublicSurvey",
        "BallotBoxStuffingPrevention": "false",
        "NoIndex": "Yes",
        "SecureResponseFiles": "true",
        "SurveyExpiration": "None",
        "SurveyTermination": "DefaultMessage",
        "Header": "",
        "Footer": "",
        "ProgressBarDisplay": "None",
        "PartialData": "+1 week",
        "ValidationMessage": "",
        "PreviousButton": "",
        "NextButton": "",
        "SurveyTitle": "Qualtrics Survey | Qualtrics Experience Management",
        "SkinLibrary": "ucdavis",
        "SkinType": "templated",
        "Skin": {
          "brandingId": None,
          "templateId": "*base",
          "overrides": {
            "questionText": {
              "size": "16px"
            },
            "answerText": {
              "size": "14px"
            },
			"layout": {
				"spacing": 0
			}
          }
        },
        "NewScoring": 1
	  }
	},
	{
      "SurveyID": "SV_eLnpGNWb3hM31cy",
      "Element": "SCO",
      "PrimaryAttribute": "Scoring",
      "SecondaryAttribute": None,
      "TertiaryAttribute": None,
      "Payload": {
        "ScoringCategories": [
          {
            "ID": "SC_0",
            "Name": "Score",
            "Description": ""
          }
        ],
        "ScoringCategoryGroups": [],
        "ScoringSummaryCategory": None,
        "ScoringSummaryAfterQuestions": 0,
        "ScoringSummaryAfterSurvey": 0,
        "DefaultScoringCategory": "SC_0",
        "AutoScoringCategory": None
      }
    },
    {
      "SurveyID": "SV_eLnpGNWb3hM31cy",
      "Element": "PROJ",
      "PrimaryAttribute": "CORE",
      "SecondaryAttribute": None,
      "TertiaryAttribute": "1.1.0",
      "Payload": {
        "ProjectCategory": "CORE",
        "SchemaVersion": "1.1.0"
      }
    },
    {
      "SurveyID": "SV_eLnpGNWb3hM31cy",
      "Element": "STAT",
      "PrimaryAttribute": "Survey Statistics",
      "SecondaryAttribute": None,
      "TertiaryAttribute": None,
      "Payload": {
        "MobileCompatible": True,
        "ID": "Survey Statistics"
      }
    },
    {
      "SurveyID": "SV_eLnpGNWb3hM31cy",
      "Element": "QC",
      "PrimaryAttribute": "Survey Question Count",
      "SecondaryAttribute": "3",
      "TertiaryAttribute": None,
      "Payload": None
    }
]

survey_info["SurveyElements"][0]["Payload"].append(
	{
		"Type": "Trash",
		"Description": "Trash / Unused Questions",
		"ID": "BL_3JCZSrANuFazQ7I",
	}
)

survey_elements = survey_info["SurveyElements"]

directions = """For each headline, we want you to: 
a) Identify whether the headline is about an acquisition or merger. 
b) if it is, for you to identify and enter (preferably by copy-pasting verbatim) the ACQUIRER and ACQUIRED companies. 
c) If the ACQUIRER or ACQUIRED names are not obvious from the headline, please leave the corresponding box blank. 
d) If there are two company names, but you don't know who acquired whom (as in the case of a merger), please still enter the names in either field. 
e) If you are not sure if the headline refers to an acquisition, or if the text does not look like a headline, please mark "not sure" or "This is not a headline". You can still enter company names if relevant.

To increase speed, we suggest using the keyboard to navigate the response:
- "Tab" moves to the next field
- You can use "Y" or "N" keys to select the corresponding drop-down field

Student ID Assignments
- Jahanvi: 0
- Meghna: 1
- Sanjana: 2
- Karina: 3\n\n
"""

# # add student ID question
# curr = 0
# qid = "QID{}".format(curr)
# student_qid = qid
# survey_elements.append({
# 	"SurveyID": "SV_eLnpGNWb3hM31cy",
# 	"Element": "SQ",
# 	"PrimaryAttribute": qid,
# 	"SecondaryAttribute": directions,
# 	"TertiaryAttribute": None,
# 	"Payload": {
# 	"QuestionText": directions,
# 	"QuestionID": qid,
# 	"QuestionType": "DB",
# 	"Selector": "TB",
# 	"QuestionDescription": directions,
# 	"Validation": {
# 	  "Settings": {
# 	    "Type": "None"
# 	  }
# 	},
# 	"Language": [],
# 	"DataExportTag": qid
# 	}
# })
# sid_elem = survey_elements[-1]

sid_choices = {}
for i in range(num_students):
	sid_choices[str(i)] = { "Display": str(i) }

sort_sid_choices = list(sid_choices.keys())
sort_sid_choices.sort()
# survey_info["SurveyElements"][0]["Payload"].append({
# 	"Type": "Standard",
# 	"SubType": "",
# 	"Description": "Block {}".format(curr),
# 	"ID": "BL_{}".format(curr),
# 	"BlockElements": [],
# 	"Options": {
# 		"BlockLocking": "false",
# 		"RandomizeQuestions": "false",
# 		"BlockVisibility": "Collapsed",
# 	}
# })
# block_elements = survey_info["SurveyElements"][0]["Payload"][1]["BlockElements"]

# survey_info["SurveyElements"][1]["Payload"]["Flow"].append(
# 	{
# 		"ID": "BL_{}".format(curr),
# 		"Type": "Block",
# 		"FlowID": "FL_{}".format(curr)
# 	}
# )

# block_elements.append({
# 	"Type": "Question",
#     "QuestionID": "QID0"
# 	})
# block_elements.append({
# 	"Type": "Page Break",
# 	})

# elem = {
# 	"QuestionText": "Student ID\n\n",
# 	"QuestionID": qid,
# 	"QuestionType": "MC",
# 	"Selector": "DL",
# 	"QuestionDescription": "Student ID",
# 	"Choices": sid_choices,
# 	"Validation": {
# 		"Settings": {
# 			"ForceResponse": "ON",
# 			"ForceResponseType": "ON",
# 			"Type":"None"
# 		}
# 	},
# 	"Language": [],
# 	"DataExportTag": qid,
# 	"SubSelector": "TX",
# 	"DataVisibility": {
# 		"Private": False,
# 		"Hidden": False
# 	},
# 	"Configuration": {
# 		"QuestionDescriptionOption": "UseText"
# 	},
# 	"ChoiceOrder": sort_sid_choices,
# 	"NextChoiceId": str(int(sort_sid_choices[len(sort_sid_choices) - 1]) + 1),
# 	"NextAnswerId": 1,
# }
# sid_elem["Payload"] = elem

num_subparts = 5

title_to_student = {}
attention_check_title_to_student = {}
training_title_to_student = {}

for student, title_idxs in student_assignments.items():
	for t in title_idxs:
		if t in title_to_student:
			title_to_student[t].append(student)
		else:
			title_to_student[t] = [student]

for a_chunk in attention_check_headlines:
	for a in a_chunk:
		attention_check_title_to_student[a] = list(range(num_students))

for t in training_headlines:
	training_title_to_student[t] = list(range(num_students))

def add_cond_display(student_qid, sids):
	q_cond_display = {
		"Type": "BooleanExpression",
		"inPage": False
	}

	q_cond_display["0"] = {"Type": "If"}
	conj = "If"
	for s in range(len(sids)):
		sid = sids[s]
		q_cond_display["0"][str(s)] = {
			"LogicType": "Question",
			"QuestionID": student_qid,
			"QuestionIsInLoop": "no",
			"ChoiceLocator": "q://{}/SelectableChoice/{}".format(student_qid, sid),
			"Operator": "Selected",
			"QuestionIDFromLocator": student_qid,
			"LeftOperand": "q://{}/SelectableChoice/{}".format(student_qid, sid),
			"Type": "Expression",
			"Description": "<span class=\"ConjDesc\">{}</span> <span class=\"QuestionDesc\">Student ID</span> <span class=\"LeftOpDesc\">{}</span> <span class=\"OpDesc\">Is Selected</span> ".format(conj, sid)
		}
		if s > 0:
			q_cond_display["0"][str(s)]["Conjuction"] = "Or"
		conj = "Or"
	return q_cond_display

def create_branch_logic(branch_logic_template, fl_id, thresh):
	branch_logic_template_copy = copy.deepcopy(branch_logic_template)
	branch_logic_template_copy["FlowID"] = "FL_{}".format(fl_id)
	# curr_end_survey_display = copy.deepcopy(end_survey_display)
	# curr_end_survey_display["Block"] = curr_end_survey_display["Block"].format(block_id)
	# curr_end_survey_display["FlowID"] = curr_end_survey_display["FlowID"].format(fl_id - 1)
	# survey_info["SurveyElements"][0]["Payload"].append({
	# 	"Type": "Standard",
	# 	"SubType": "",
	# 	"Description": "Block {}".format(block_id),
	# 	"ID": "BL_{}".format(block_id),
	# 	"BlockElements": [
	# 		{
	# 			"Type": "Question",
	# 			"QuestionID": "QID{}".format(block_id - 1),
	# 		}
	# 	],
	# 	"Options": {
	# 		"BlockLocking": "false",
	# 		"RandomizeQuestions": "false",
	# 		"BlockVisibility": "Collapsed",
	# 	}
	# })
	branch_logic_template_copy["Flow"] = [end_survey]
	branch_logic_template_copy["BranchLogic"]["0"]["0"]["RightOperand"] = str(thresh)
	branch_logic_template_copy["BranchLogic"]["0"]["0"]["Description"] = "<span class=\"ConjDesc\">If</span>  <span class=\"LeftOpDesc\">Score</span> <span class=\"OpDesc\">Is Less Than</span> <span class=\"RightOpDesc\"> {} </span>".format(thresh)
	return branch_logic_template_copy

def add_score(elem, train_ans = -1):
	if train_ans != -1:
		elem["Payload"]["GradingData"] = [
			{
				"ChoiceID": "1",
				"Grades": {
					"SC_0": 0
				},
				"index": 0
			},
			{
				"ChoiceID": "2",
				"Grades": {
					"SC_0": 0
				},
				"index": 1
			},
			{
				"ChoiceID": "3",
				"Grades": {
					"SC_0": 0
				},
				"index": 2
			},
			{
				"ChoiceID": "4",
				"Grades": {
					"SC_0": 0
				},
				"index": 3
			}
		]
		elem["Payload"]["GradingData"][train_ans]["Grades"]["SC_0"] = 1

def create_question(curr_title, curr, disp_settings = [], train_ans = -1):
	qid = "QID{}".format(curr)

	survey_info["SurveyElements"][0]["Payload"].append({
		"Type": "Standard",
		"SubType": "",
		"Description": "Block {}".format(curr),
		"ID": "BL_{}".format(curr),
		"BlockElements": [],
		"Options": {
			"BlockLocking": "false",
			"RandomizeQuestions": "false",
			"BlockVisibility": "Collapsed",
		}
	})
	block_elements = survey_info["SurveyElements"][0]["Payload"][curr]["BlockElements"]
	
	# append to flow payload
	survey_info["SurveyElements"][1]["Payload"]["Flow"].append(
		{
			"ID": "BL_{}".format(curr),
			"Type": "Block",
			"FlowID": "FL_{}".format(curr)
		}
	)

	for subpart in range(num_subparts):
		curr_sub = (curr - 2) * num_subparts + subpart + 1
		qid = "QID{}".format(curr_sub)

		block_elements.append({
			"Type": "Question",
			"QuestionID": qid,
		})

		if subpart == 0:
			elem = {
		      "SurveyID": "SV_eLnpGNWb3hM31cy",
		      "Element": "SQ",
		      "PrimaryAttribute": qid,
		      "SecondaryAttribute": "{}. Headline: {}".format(curr - 1, curr_title),
		      "TertiaryAttribute": None,
		      "Payload": {
		        "QuestionText": "{}. Headline: <br><br>\n<b>{}</b>\n".format(curr - 1, curr_title),
		        "QuestionID": qid,
		        "QuestionType": "DB",
		        "Selector": "TB",
		        "QuestionDescription": curr_title,
		        "Validation": {
		          "Settings": {
		            "Type": "None"
		          }
		        },
		        "Language": [],
		        "DataExportTag": qid
		      }
			}
		elif subpart == 1:
			elem = {
				"SurveyID": "SV_eLnpGNWb3hM31cy",
				"Element": "SQ",
				"PrimaryAttribute": qid,
				"SecondaryAttribute": "Do you think that this headline refers to an acquisition or merger?",
				"TertiaryAttribute": None,
				"Payload": {
					"QuestionText": "Do you think that this headline refers to an acquisition or merger?\n\n",
					"QuestionID": qid,
					"DataExportTag": qid,
					"QuestionType": "MC",
					"Selector": "DL",
					"Configuration": {
						"QuestionDescriptionOption": "UseText"
					},
					"QuestionDescription": "Do you think that this headline refers to an acquisition or merger?",
					"Choices": {
						"1": {
							"Display": "Yes"
						},
						"2": {
							"Display": "No"
						},
						"3": {
							"Display": "Not sure"
						},
						"4": {
							"Display": "Not a headline"
						}
					},
					"ChoiceOrder": [
						"1",
						"2",
						"3",
						"4",
					],
					"Validation": {
						"Settings": {
							"ForceResponse": "ON",
							"ForceResponseType": "ON",
							"Type":"None"
						}
					},
					"GradingData": [],
					"Language": [],
					"NextChoiceId": 5,
        			"NextAnswerId": 1,
					"QuestionID": qid
				},
			}

			add_score(elem, train_ans)
		elif subpart == 2:
			elem = {
				"SurveyID": "SV_eLnpGNWb3hM31cy",
				"Element": "SQ",
				"PrimaryAttribute": qid,
				"SecondaryAttribute": "ACQUIRER (leave blank if not indicated or unclear):",
				"TertiaryAttribute": None,
				"Payload": {
					"QuestionText": "ACQUIRER (leave blank if not indicated or unclear):\n\n",
					"DefaultChoices": False,
					"QuestionID": qid,
					"QuestionType": "TE",
					"Selector": "SL",
					"Configuration": {
						"QuestionDescriptionOption": "UseText"
					},
					"QuestionDescription": "ACQUIRER (leave blank if not indicated or unclear):",
					"Validation": {
						"Settings": {
							"ForceResponse": "OFF",
							"Type": "None"
						}
					},
					"GradingData": [],
					"Language": [],
					"NextChoiceId": 4,
        			"NextAnswerId": 1,
					"SearchSource": {
						"AllowFreeResponse": "false"
					},
					"DataExportTag": qid,
				}
		    }
		elif subpart == 3:
			elem = {
				"SurveyID": "SV_eLnpGNWb3hM31cy",
				"Element": "SQ",
				"PrimaryAttribute": qid,
				"SecondaryAttribute": "ACQUIRED (leave blank if not indicated or unclear):",
				"TertiaryAttribute": None,
				"Payload": {
					"QuestionText": "ACQUIRED (leave blank if not indicated or unclear):\n\n",
					"DefaultChoices": False,
					"QuestionID": qid,
					"QuestionType": "TE",
					"Selector": "SL",
					"Configuration": {
						"QuestionDescriptionOption": "UseText"
					},
					"QuestionDescription": "ACQUIRED (leave blank if not indicated or unclear):",
					"Validation": {
						"Settings": {
							"ForceResponse": "OFF",
							"Type": "None"
						}
					},
					"GradingData": [],
					"Language": [],
					"NextChoiceId": 4,
        			"NextAnswerId": 1,
					"SearchSource": {
						"AllowFreeResponse": "false"
					},
					"DataExportTag": qid,
				}
		    }
		elif subpart == 4:
			elem = {
		      "SurveyID": "SV_eLnpGNWb3hM31cy",
		      "Element": "SQ",
		      "PrimaryAttribute": qid,
		      "SecondaryAttribute": "Timing",
		      "TertiaryAttribute": None,
		      "Payload": {
		        "QuestionText": "Timing",
		        "DefaultChoices": False,
		        "DataExportTag": qid,
		        "QuestionType": "Timing",
		        "Selector": "PageTimer",
		        "Configuration": {
		          "QuestionDescriptionOption": "UseText",
		          "MinSeconds": "0",
		          "MaxSeconds": "0"
		        },
		        "QuestionDescription": "Timing",
		        "Choices": {
		          "1": {
		            "Display": "First Click"
		          },
		          "2": {
		            "Display": "Last Click"
		          },
		          "3": {
		            "Display": "Page Submit"
		          },
		          "4": {
		            "Display": "Click Count"
		          }
		        },
		        "GradingData": [],
		        "Language": [],
		        "NextChoiceId": 4,
		        "NextAnswerId": 1,
		        "QuestionID": qid
		      }
		    }

		elem["Payload"]["DisplayLogic"] = add_cond_display("QID{}".format(0), disp_settings)
		survey_elements.append(elem)
	
	block_elements.append({
		"Type": "Page Break"
	})

# start with all training headlines
curr = 1
for t in list(training_title_to_student.keys()):
	create_question(t, curr, list(range(num_students)), training_answers[curr - 2])
	curr += 1

# set score embedded data
flow_elements = survey_elements[1]["Payload"]["Flow"]
flow_elements.append(set_score)

# add branch logic to kick respondent out of survey after training q's
training_thresh_num = math.ceil(training_thresh * training_length)
fl_id = -1
flow_elements.append(create_branch_logic(branch_logic_template, fl_id, training_thresh_num))
fl_id -= 2

num_blocks = len(attention_check_headlines)

for i in range(num_blocks):
	# in every iteration
	# pick attention check number of attention check headlines
	curr_at_check = attention_check_headlines[i]

	# pick block size - attention check number of regular headlines
	regular_headline_idxes = {}
	regular_headline_to_student = {}
	curr_headlines = set(curr_at_check)
	for j in range(num_students):
		if len(student_assignments[j]) >= block_size - len(curr_at_check):
			regular_headline_idxes[j] = np.random.choice(student_assignments[j], size = block_size - len(curr_at_check), replace = False)
		elif len(student_assignments[j]) > 0:
			regular_headline_idxes[j] = student_assignments[j]
		else:
			continue
		student_assignments[j] = list(set(student_assignments[j]) - set(regular_headline_idxes[j])) # remove the chosen headline idxes
		regular_headlines = titles[np.array(regular_headline_idxes[j])]
		curr_headlines = curr_headlines.union(set(regular_headlines))
		for r in regular_headlines:
			if r in regular_headline_to_student:
				regular_headline_to_student[r].append(j)
			else:
				regular_headline_to_student[r] = [j]
	
	# shuffle attention check and regular headlines in a block
	np.random.shuffle(np.array(list(curr_headlines)))

	for c in curr_headlines:
		if c in regular_headline_to_student:
			# special display settings
			create_question(c, curr, regular_headline_to_student[c])
		else:
			create_question(c, curr, list(range(num_students)), attention_check_answers[c][0])
		curr += 1

	# set score embedded data
	flow_elements.append(set_score)

	attention_thresh_num = training_thresh_num + sum(calc_attention_thresh[:i + 1])
	flow_elements.append(create_branch_logic(branch_logic_template, fl_id, attention_thresh_num))
	fl_id -= 2

# create the rest of the questions for the remaining regular headlines
for student, remaining in student_assignments.items():
	for r in remaining:
		# special display settings
		create_question(titles[r], curr, title_to_student[r])
		curr += 1

with open(qsf_name, 'w') as f:
	json.dump(survey_info, f, ensure_ascii = False, indent = 2)

# test that all headlines in the MTurk dump are displayed to at least one user
curr_idx = 0
mturk_survey_q_dump = survey_elements[7:]
headlines_displayed = {}
while curr_idx < len(mturk_survey_q_dump):
	curr_headline = mturk_survey_q_dump[curr_idx]["Payload"]["QuestionDescription"]
	curr_idx += num_subparts
	if curr_headline in headlines_displayed:
		headlines_displayed[curr_headline] += 1
	else:
		headlines_displayed[curr_headline] = 1

assert(len(set(headlines_displayed.keys())) == num_headlines + training_length + len(attention_check_headlines) * attention_check_length)