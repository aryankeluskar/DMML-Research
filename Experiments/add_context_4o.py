import os
from openai import OpenAI
import dotenv
dotenv.load_dotenv()

# start time
import time
start = time.time()

client = OpenAI(
  api_key=os.environ.get("DMML_API_KEY"),
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "",
        }
    ],
    model="gpt-4o",
)

str(chat_completion.choices[0].message.content)

# go through sample.json and ask questions to gpt
import json
all_qs = json.load(open("data/filtered_train.json"))

# randomly sample 0 questions
# import random
# sample = random.sample(all_qs, 1000)

# load mini_sample_input_1729208141.json to maintain consistency
sample = json.load(open("Experiments/mini_sample_input_1729208141.json"))

# store the sample input into sample_input_<current_unix_time>.json
import time
current_unix_time = int(time.time())
with open(f"Experiments/mini_low_temp_add_context_input_{current_unix_time}.json", "w") as f:
    json.dump(sample, f)

count = 0
out = []
for i in sample:
    count += 1
    print(f"Question {count}")

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Add extra information to the following question. Also specify the current month and year is January 2018, so answer questions accordingly. Your aim is to disambiguate what it is asking: {i['nq_question']}",    
            }
        ],
        model="gpt-4o"
    )

    add_context = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Answer the question as concisely as possible with ONLY one answer without any other text:  {chat_completion.choices[0].message.content}",
            }
        ],
        model="gpt-4o"
    )

    # print(f"\t\tAnswer: \t {baseline.choices[0].message.content}")
    # print("\t\tGround Truth: \t", i['nq_answer'])

    curr = {
        "data_id": i["nq_id"],
        "ambig_question": i["nq_question"],
        "disambig_question": chat_completion.choices[0].message.content,
        "llm_response": add_context.choices[0].message.content,
        "ground_truth": i["nq_answer"],
    }

    out.append(curr)

    # store the output into sample_output_<current_unix_time>.json
    with open(f"Experiments/o_add_context_output_{current_unix_time}.json", "w") as f:
        json.dump(out, f)


# 1000 questions took 2.82 dollars, 1 hour and 34.163475036621 seconds to complete

# end time and save in add_context_4o.txt
end = time.time()
with open("Experiments/add_context_4o.txt", "w") as f:
    f.write(f"1000 questions took {end - start} seconds to complete")