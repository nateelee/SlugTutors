// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        add_mode: false,
        post_content: "",
        rows: [],
        average: 0,
        the_tutor_id: 0,
        rating_number: 0,
        edit_rating_number: 0,
    };

    app.enumerate = (a) => {
        let k = 0;
        a.map((e) => { e._idx = k++; });
        return a;
    };

    app.complete = (rows) => {
        rows.map((p) => {
            p.rating = 0;
            p.rater_id = "";
            p.average = 0;
            // p.num_likes = 0;
            // p.num_dislikes = 0;
        })
    };



    app.get_rating = async(postid) => {
        const ratings = await axios.post(get_rating_url, { post_id: postid }).then(response => response.data)
        app.data.thumbs = {...app.data.thumbs, [postid]: ratings }
    };

    app.set_rating = (postid, rating, previous_rating) => {
        const obj = app.vue.rows.find(element => element.id == postid)
        if (rating == -1) {
            if (previous_rating == 1) {
                obj.num_likes--;
            }
            obj.num_dislikes++;
        } else if (rating == 1) {
            if (previous_rating == -1) {
                obj.num_dislikes--;
            }
            obj.num_likes++;
        } else if (rating == 0) {
            if (previous_rating == -1) {
                obj.num_dislikes--;
            } else if (previous_rating == 1) {
                obj.num_likes--;
            }
        }
        app.vue.rows = [...app.vue.rows]
        axios.post(set_rating_url, { post_id: postid, rating, num_likes: obj.num_likes, num_dislikes: obj.num_dislikes }).then(response => response.data).then(results => {
            app.data.rows = [...app.data.rows.map(post => post.id == postid ? {...post, my_thumb: rating } : post)]
            app.data.thumbs = {...app.data.thumbs, [postid]: results }

        })

    };

    app.decorate = (a) => {
        a.forEach((e) => {
            e._state = "clean";
            e._server_vals = { post: e.post };
            e.is_being_editted = false;
        });
        return a;
    };

    app.add_post = function() {
        axios.post(add_post_url, {
            tutor_id: app.vue.the_tutor_id,
            post_body: app.vue.post_content,
            rating_number: app.vue.rating_number,

        }).then(function(response) {
            app.vue.average = response.data.average;
            app.vue.rows.push({
                id: response.data.id,
                post_body: app.vue.post_content,
                name: response.data.name,
                is_my_post: true,
                rating_number: app.vue.rating_number,
                _state: "clean",
                num_likes: 0,
                num_dislikes: 0,
                is_being_editted: false,
            });
            app.enumerate(app.vue.rows);
            app.reset_form();
            app.set_add_status(false);
            app.vue.rating_number = 0;
        });
    };

    app.add_edit_rating = function(row_idx) {
        let row = app.vue.rows[row_idx];
        axios.post(update_rating_url, {
            post_id: row.id,
            tutor_id: app.vue.the_tutor_id,
            post_body: row.post_body,
            rating_number: app.vue.edit_rating_number,

        }).then(function(response) {
            app.vue.average = response.data.average;

            row.rating_number = app.vue.edit_rating_number;

            app.edit_rating(row_idx, false);
            app.vue.edit_rating_number = 0;
        });
    };

    app.reset_form = function() {
        app.vue.post_content = "";
    };

    app.delete_post = function(row_idx) {
        let id = app.vue.rows[row_idx].id;
        axios.get(delete_post_url, { params: { id: id } }).then(function(response) {
            app.vue.average = response.data.average;
            for (let i = 0; i < app.vue.rows.length; i++) {
                if (app.vue.rows[i].id === id) {
                    app.vue.rows.splice(i, 1);
                    app.enumerate(app.vue.rows);
                    break;
                }
            }
        });
    };

    app.edit_rating = function(r_idx, new_status) {
        let row = app.vue.rows[r_idx];
        row.is_being_editted = new_status;
    };

    app.set_add_status = function(new_status) {
        app.vue.add_mode = new_status;
    };

    app.start_edit = function(row_idx) {
        app.vue.rows[row_idx]._state = "edit";
    };


    app.stop_edit = function(row_idx) {
        let row = app.vue.rows[row_idx];
        if (row._state === 'edit') {
            row._state = "clean";
            axios.post(edit_contact_url, {
                id: row.id,
                value: row.post_body
            })
        }
    };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        add_post: app.add_post,
        set_add_status: app.set_add_status,
        delete_post: app.delete_post,
        get_rating: app.get_rating,
        set_rating: app.set_rating,
        start_edit: app.start_edit,
        stop_edit: app.stop_edit,
        edit_rating: app.edit_rating,
        add_edit_rating: app.add_edit_rating

    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    app.init = () => {
        app.vue.the_tutor_id = tutor_id;
        axios.get(load_posts_url, { params: { the_tutor_id: tutor_id } })
            .then((result) => {
                let rows = result.data.rows;
                app.vue.rows = app.decorate(app.enumerate(result.data.rows));
                app.enumerate(rows);
                app.complete(rows);
                app.vue.rows = rows;
                app.vue.average = result.data.average
            })
            .then(() => {
                for (let r of app.vue.rows) {
                    axios.get(get_rating_url, { params: { "post_id": r.id } })
                        .then((result) => {
                            r.rater_id = result.data.rater_id;
                            r.rating = result.data.rating;
                        });
                }

            });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);