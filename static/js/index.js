// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // filter represents main page filter state
    // filter.classes maps class id to "filtered?"
    // all false => no filter applied.
    let filter = {
        classes: {
            ...classes,
        },
    };
    for (class_id in filter.classes) {
        filter.classes[class_id] = false;
    }

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        tutor_list: [],
        selected_tutor: {},
        is_selected: false,
        classes,
        filter,
    };

    app.watch = {
        filter: {
            handler: (filter) => {
                console.log("a");
                app.get_tutors(filter.classes);
            },
            deep: true,
        },
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {
            e._idx = k++;
        });
        return a;
    };

    app.add_classes = (a) => {
        // This adds an _idx field to each element of the array.

        a.map((e) => {
            e.classes = [];
            e.class_history = [];
        });
        return a;
    };

    app.toggle_select = function (profile_index) {
        let profile = app.vue.tutor_list[profile_index];
        app.vue.is_selected = true;
        app.vue.selected_tutor = profile;
    };

    app.get_tutors = (classes) => {
        query = Object.keys(classes)
            .filter((key) => classes[key])
            .join(",");

        axios
            .get(get_tutors_url, {
                params: {
                    classes: query === "" ? undefined : query,
                },
            })
            .then(function (response) {
                let tutor_list = response.data.tutor_list;

                app.enumerate(tutor_list);
                app.add_classes(tutor_list);
                app.vue.tutor_list = tutor_list;
            })
            .then(() => {
                for (let tutor of app.vue.tutor_list) {
                    axios
                        .get(get_tutor_classes_url, {
                            params: { tutor_id: tutor.id },
                        })
                        .then(function (result) {
                            classes_tutored = result.data.classes_tutored;
                            tutor.classes = classes_tutored;
                        });
                    axios
                        .get(get_tutor_class_history_url, {
                            params: { tutor_id: tutor.id },
                        })
                        .then(function (result) {
                            class_history = result.data.class_history;
                            tutor.class_history = class_history;
                        });
                }
            });
    };

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        toggle_select: app.toggle_select,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods,
        watch: app.watch,
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
        app.get_tutors({});
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
