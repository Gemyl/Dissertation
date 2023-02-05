function addField() {
    const uniqVal = new Uint32Array(1);
    crypto.getRandomValues(uniqVal);
    var survey_options = document.getElementById("add_new_field");
    var container = document.createElement("div");

    var inputField = document.createElement("input");
    inputField.setAttribute("size", 50);
    inputField.setAttribute("type", "text");
    inputField.setAttribute("id", "input"+uniqVal[0]);
    inputField.setAttribute("class", "survey_options");
    inputField.setAttribute("name", "input"+uniqVal[0]);
    inputField.setAttribute("placeholder", "Enter Keyword");

    var remButton = document.createElement("button");
    remButton.type = "button";
    remButton.textContent = "X";
    remButton.style.color = "white";
    remButton.style.fontWeight = "bold";
    remButton.style.backgroundColor = "black";

    var selectField = document.createElement("select");
    selectField.size = "50px";
    selectField.setAttribute("id", "select"+uniqVal[0]);
    selectField.setAttribute("name", "select"+uniqVal[0]);

    var option_1 = document.createElement("option");
    var option_2 = document.createElement("option");
    var option_3 = document.createElement("option");

    option_1.text = "AND";
    option_1.setAttribute("value", "AND");
    option_1.setAttribute("selected", "selected");
    option_1.setAttribute("id", "option1"+uniqVal[0]);
    option_1.setAttribute("name", "option1"+uniqVal[0]);

    option_2.text = "OR";
    option_2.setAttribute("value", "OR");
    option_2.setAttribute("id", "option2"+uniqVal[0]);
    option_2.setAttribute("name", "option2"+uniqVal[0]);

    option_3.text = "NOT";
    option_3.setAttribute("value", "NOT");    
    option_3.setAttribute("id", "option3"+uniqVal[0]);
    option_3.setAttribute("name", "option3"+uniqVal[0]);

    selectField.appendChild(option_1);
    selectField.appendChild(option_2);
    selectField.appendChild(option_3);

    container.appendChild(selectField);
    container.appendChild(inputField);
    container.appendChild(remButton);

    survey_options.appendChild(container);

    remButton.onclick = function() {
        this.parentElement.remove();
        moveChildrenUp();
    }

    function moveChildrenUp() {
        var children = survey_options.children;
        for (var i = 0; i < children.length; i++) {
            children[i].style.marginTop = (i * 20) + "px";
        }
    }
}